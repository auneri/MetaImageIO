import io
import pathlib
import zlib

import numpy as np


# http://www.itk.org/Wiki/ITK/MetaIO/Documentation
MHD_TAGS = (
    'Comment',                  # MET_STRING
    'ObjectType',               # MET_STRING (Image)
    'ObjectSubType',            # MET_STRING
    'TransformType',            # MET_STRING (Rigid)
    'NDims',                    # MET_INT
    'Name',                     # MET_STRING
    'ID',                       # MET_INT
    'ParentID',                 # MET_INT
    'CompressedData',           # MET_STRING (boolean)
    'CompressedDataSize',       # MET_INT
    'BinaryData',               # MET_STRING (boolean)
    'BinaryDataByteOrderMSB',   # MET_STRING (boolean)
    'ElementByteOrderMSB',      # MET_STRING (boolean)
    'Color',                    # MET_FLOAT_ARRAY[4]
    'Position',                 # MET_FLOAT_ARRAY[NDims]
    'Offset',                   # == Position
    'Origin',                   # == Position
    'Orientation',              # MET_FLOAT_MATRIX[NDims][NDims]
    'Rotation',                 # == Orientation
    'TransformMatrix',          # == Orientation
    'CenterOfRotation',         # MET_FLOAT_ARRAY[NDims]
    'AnatomicalOrientation',    # MET_STRING (RAS)
    'ElementSpacing',           # MET_FLOAT_ARRAY[NDims]
    'DimSize',                  # MET_INT_ARRAY[NDims]
    'HeaderSize',               # MET_INT
    'HeaderSizePerSlice',       # MET_INT (non-standard tag for handling per slice header)
    'Modality',                 # MET_STRING (MET_MOD_CT)
    'SequenceID',               # MET_INT_ARRAY[4]
    'ElementMin',               # MET_FLOAT
    'ElementMax',               # MET_FLOAT
    'ElementNumberOfChannels',  # MET_INT
    'ElementSize',              # MET_FLOAT_ARRAY[NDims]
    'ElementType',              # MET_STRING (MET_UINT)
    'ElementDataFile')          # MET_STRING

MHD_TYPES = {
    'MET_CHAR': np.int8,
    'MET_UCHAR': np.uint8,
    'MET_SHORT': np.int16,
    'MET_USHORT': np.uint16,
    'MET_INT': np.int32,
    'MET_UINT': np.uint32,
    'MET_LONG': np.int64,
    'MET_ULONG': np.uint64,
    'MET_FLOAT': np.float32,
    'MET_DOUBLE': np.float64}


def read_image(filepath, slices=None, memmap=False):
    filepath = pathlib.Path(filepath)

    # read header from file
    header_in = {}
    header_size = 0
    islist = False
    islocal = False
    with filepath.open('rb') as f:
        for line in f:
            line = line.decode()
            header_size += len(line)
            # skip empty and commented lines
            if not line or line.startswith('#'):
                continue
            key = line.split('=', 1)[0].strip()
            value = line.split('=', 1)[-1].strip()
            # handle case variations
            try:
                key = MHD_TAGS[[x.upper() for x in MHD_TAGS].index(key.upper())]
                header_in[key] = value
            except ValueError:
                pass
            # handle supported ElementDataFile formats
            if islist:
                header_in['ElementDataFile'].append(line.strip())
            elif key == 'ElementDataFile' and value.upper() == 'LIST':
                header_in['ElementDataFile'] = []
                islist = True
            elif key == 'ElementDataFile' and value.upper() == 'LOCAL':
                header_in['ElementDataFile'] = [str(filepath)]
                islocal = True
                break
            elif key == 'ElementDataFile' and '%' in value:
                args = value.split()
                header_in['ElementDataFile'] = [args[0] % i for i in range(int(args[1]), int(args[2]) + int(args[3]), int(args[3]))]
            elif key == 'ElementDataFile':
                header_in['ElementDataFile'] = [value]

    # typecast header tags to native types
    header = dict.fromkeys(MHD_TAGS, None)
    for key, value in header_in.items():
        if key in ('Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality', 'ElementDataFile'):
            header[key] = value
        elif key in ('NDims', 'ID', 'ParentID', 'CompressedDataSize', 'HeaderSize', 'HeaderSizePerSlice', 'ElementNumberOfChannels'):
            header[key] = np.intp(value)
        elif key in ('CompressedData', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB'):
            header[key] = value.upper() == 'TRUE'
        elif key in ('Color', 'Position', 'Offset', 'Origin', 'CenterOfRotation', 'ElementSpacing', 'ElementSize'):
            header[key] = np.array(value.split(), dtype=float)
        elif key in ('Orientation', 'Rotation', 'TransformMatrix'):
            header[key] = np.array(value.split(), dtype=float).reshape(3, 3)
        elif key in ('DimSize', 'SequenceID'):
            header[key] = np.array(value.split(), dtype=int)
        elif key in ('ElementMin', 'ElementMax'):
            header[key] = float(value)
        elif key == 'ElementType':
            try:
                header[key] = [x[1] for x in MHD_TYPES.items() if x[0] == value.upper()][0]
            except IndexError:
                raise IOError(f'ElementType "{value}" is not supported')

    # read image from file
    shape = np.array(header['DimSize'][::-1])
    if (header.get('ElementNumberOfChannels') or 1) > 1:
        shape = np.r_[shape, header['ElementNumberOfChannels']]
    element_size = np.dtype(header['ElementType']).itemsize
    if memmap:
        if header.get('BinaryDataByteOrderMSB') or header.get('ElementByteOrderMSB'):
            raise IOError('ByteOrderMSB is not supported with memmap')
        if header.get('CompressedData'):
            raise IOError('CompressedData is not supported with memmap')
        if header['HeaderSizePerSlice'] is not None:
            raise IOError('HeaderSizePerSlice is not supported with memmap')
        if len(header['ElementDataFile']) != 1:
            raise IOError('Only single ElementDataFile is supported with memmap')
        if slices:
            raise IOError('Specifying slices is not supported with memmap')
        datapath = pathlib.Path(header['ElementDataFile'][0])
        if not datapath.is_absolute():
            datapath = filepath.parent / datapath
        offset = 0
        if islocal:
            offset += header_size
        offset += header.get('HeaderSize') or 0
        image = np.memmap(datapath, dtype=header['ElementType'], mode='c', offset=offset, shape=tuple(shape))
    else:
        increment = np.prod(shape[1:], dtype=np.intp) * np.intp(element_size)
        if slices is None:
            slices = range(shape[0])
        slices = tuple(slices)
        if np.any(np.diff(slices) <= 0):
            raise IOError('Slices must be strictly increasing')
        if slices and (slices[0] < 0 or slices[-1] >= shape[0]):
            raise IOError('Slices must be bounded by z dimension')
        if len(header['ElementDataFile']) > 1:
            shape[0] = 1
        data = io.BytesIO()

        for i, datapath in enumerate(header['ElementDataFile']):
            datapath = pathlib.Path(datapath)
            if not datapath.is_absolute():
                datapath = filepath.parent / datapath
            with datapath.open('rb') as f:
                if islocal:
                    f.seek(header_size, 1)
                f.seek((header.get('HeaderSize') or 0), 1)
                if header.get('CompressedData'):
                    if header['CompressedDataSize'] is None:
                        raise IOError('CompressedDataSize needs to be specified when using CompressedData')
                    if header['HeaderSizePerSlice'] is not None:
                        raise IOError('HeaderSizePerSlice is not supported with compressed images')
                    if len(header['ElementDataFile']) == 1 and slices != tuple(range(shape[0])):
                        raise IOError('Specifying slices with compressed images is not supported')
                    data.write(zlib.decompress(f.read(header['CompressedDataSize'])))
                else:
                    read, seek = np.intp(0), np.intp(0)
                    for j in range(shape[0]):
                        if header['HeaderSizePerSlice'] is not None:
                            data.write(f.read(read))
                            read = np.intp(0)
                            seek += header['HeaderSizePerSlice']
                        if (len(header['ElementDataFile']) == 1 and j in slices) or (len(header['ElementDataFile']) > 1 and i in slices):
                            f.seek(seek, 1)
                            seek = np.intp(0)
                            read += increment
                            if read > np.iinfo(np.intp).max - increment:
                                data.write(f.read(read))
                                read = np.intp(0)
                        else:
                            data.write(f.read(read))
                            read = np.intp(0)
                            seek += increment
                            if seek > np.iinfo(np.intp).max - increment:
                                f.seek(seek, 1)
                                seek = np.intp(0)
                    data.write(f.read(read))
        if slices:
            shape[0] = len(slices)
            image = np.frombuffer(data.getbuffer(), dtype=header['ElementType']).reshape(shape)
            if header.get('BinaryDataByteOrderMSB') or header.get('ElementByteOrderMSB'):
                image.byteswap(True)
        else:
            image = None

    # remove unused tags from header
    header = {x: y for x, y in header.items() if y is not None}
    if isinstance(header['ElementDataFile'], (tuple, list)):
        header['ElementDataFile'] = header['ElementDataFile'][0]

    return image, header


def write_image(filepath, image=None, **kwargs):
    filepath = pathlib.Path(filepath)

    # initialize header
    header = dict.fromkeys(MHD_TAGS, None)
    header['ObjectType'] = 'Image'
    header['NDims'] = 3
    header['BinaryData'] = True
    header['BinaryDataByteOrderMSB'] = False
    header['ElementSpacing'] = np.ones(3)
    header['DimSize'] = np.zeros(3, np.int)
    header['ElementType'] = float
    if image is not None:
        header['NDims'] = np.ndim(image)
        header['ElementSpacing'] = np.ones(np.ndim(image))
        header['DimSize'] = np.shape(image)[::-1]
        header['ElementType'] = np.asarray(image).dtype

    # overwrite input header tags (case incensitive)
    for key, value in kwargs.items():
        try:
            key = MHD_TAGS[[x.upper() for x in MHD_TAGS].index(key.upper())]
        except ValueError:
            pass
        else:
            header[key] = value

    # define ElementDataFile
    if header['ElementDataFile'] is None:
        if filepath.suffix == '.mha':
            header['ElementDataFile'] = 'LOCAL'
        else:
            header['ElementDataFile'] = str(filepath.with_suffix('.zraw' if header.get('CompressedData') else '.raw'))

    # prepare image for saving
    if image is not None:
        if header['ElementDataFile'].upper() == 'LOCAL':
            datapaths = [str(filepath)]
            mode = 'ab'
        elif isinstance(header['ElementDataFile'], (tuple, list)):
            datapaths = header['ElementDataFile']
            mode = 'wb'
            if np.ndim(image) != 3 or np.shape(image)[2] != len(datapaths):
                raise IOError('Number filenames does not match number of slices')
        else:
            datapaths = [header['ElementDataFile']]
            mode = 'wb'

    # typecast header tags to string
    header_out = {}
    for key, value in header.items():
        if value is None:
            continue
        elif key in ('Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality'):
            header_out[key] = value
        elif key in ('NDims', 'ID', 'ParentID', 'CompressedData', 'CompressedDataSize', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB', 'HeaderSize', 'HeaderSizePerSlice', 'ElementMin', 'ElementMax', 'ElementNumberOfChannels'):
            header_out[key] = str(value)
        elif key in ('Color', 'Position', 'Offset', 'Origin', 'Orientation', 'Rotation', 'TransformMatrix', 'CenterOfRotation', 'ElementSpacing', 'DimSize', 'SequenceID', 'ElementSize'):
            header_out[key] = ' '.join(str(x) for x in np.ravel(value))
        elif key == 'ElementType':
            try:
                header_out[key] = [x[0] for x in MHD_TYPES.items() if np.issubdtype(value, x[1])][0]
            except IndexError:
                raise IOError(f'ElementType "{value}" is not supported')
        elif key == 'ElementDataFile':
            if isinstance(value, (tuple, list)):
                header_out[key] = 'LIST'
                for i in value:
                    header_out[key] += f'\n{i}'
            else:
                header_out[key] = value
        else:
            raise IOError(f'Header tag "{key}" is not recognized')

    # write header to file
    with filepath.open('w') as f:
        for key, value in header_out.items():
            f.write(f'{key} = {value}\n')

    # write image to file
    if image is not None:
        if header.get('CompressedData'):
            header['CompressedDataSize'] = 0
        for i, datapath in enumerate(datapaths):
            datapath = pathlib.Path(datapath)
            if not datapath.is_absolute():
                datapath = filepath.parent / datapath
            data = image[i] if len(datapaths) > 1 else image
            if header.get('BinaryDataByteOrderMSB') or header.get('ElementByteOrderMSB'):
                data.byteswap(True)
            data = data.astype(header['ElementType']).tobytes()
            if header.get('CompressedData'):
                data = zlib.compress(data)
                header['CompressedDataSize'] += len(data)
            with datapath.open(mode) as f:
                f.write(data)

    # remove unused tags from header
    header = {x: y for x, y in header.items() if y is not None}

    return header
