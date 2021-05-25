import io
import pathlib
import zlib

import numpy as np


# https://itk.org/Wiki/ITK/MetaIO/Documentation#Reference:_Tags_of_MetaImage
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

    # read metadata from file
    meta_in = {}
    meta_size = 0
    islist = False
    islocal = False
    with filepath.open('rb') as f:
        for line in f:
            line = line.decode()
            meta_size += len(line)
            # skip empty and commented lines
            if not line or line.startswith('#'):
                continue
            key = line.split('=', 1)[0].strip()
            value = line.split('=', 1)[-1].strip()
            # handle case variations
            try:
                key = MHD_TAGS[[x.upper() for x in MHD_TAGS].index(key.upper())]
                meta_in[key] = value
            except ValueError:
                pass
            # handle supported ElementDataFile formats
            if islist:
                meta_in['ElementDataFile'].append(line.strip())
            elif key == 'ElementDataFile' and value.upper() == 'LIST':
                meta_in['ElementDataFile'] = []
                islist = True
            elif key == 'ElementDataFile' and value.upper() == 'LOCAL':
                meta_in['ElementDataFile'] = [str(filepath)]
                islocal = True
                break
            elif key == 'ElementDataFile' and '%' in value:
                args = value.split()
                meta_in['ElementDataFile'] = [args[0] % i for i in range(int(args[1]), int(args[2]) + int(args[3]), int(args[3]))]
            elif key == 'ElementDataFile':
                meta_in['ElementDataFile'] = [value]

    # typecast metadata to native types
    meta = dict.fromkeys(MHD_TAGS, None)
    for key, value in meta_in.items():
        if key in ('Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality', 'ElementDataFile'):
            meta[key] = value
        elif key in ('NDims', 'ID', 'ParentID', 'CompressedDataSize', 'HeaderSize', 'HeaderSizePerSlice', 'ElementNumberOfChannels'):
            meta[key] = np.uintp(value)
        elif key in ('CompressedData', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB'):
            meta[key] = value.upper() == 'TRUE'
        elif key in ('Color', 'Position', 'Offset', 'Origin', 'CenterOfRotation', 'ElementSpacing', 'ElementSize'):
            meta[key] = np.array(value.split(), dtype=float)
        elif key in ('Orientation', 'Rotation', 'TransformMatrix'):
            meta[key] = np.array(value.split(), dtype=float).reshape(3, 3)
        elif key in ('DimSize', 'SequenceID'):
            meta[key] = np.array(value.split(), dtype=int)
        elif key in ('ElementMin', 'ElementMax'):
            meta[key] = float(value)
        elif key == 'ElementType':
            try:
                meta[key] = [x[1] for x in MHD_TYPES.items() if x[0] == value.upper()][0]
            except IndexError as exception:
                raise ValueError(f'ElementType "{value}" is not supported') from exception

    # read image from file
    shape = meta['DimSize'].copy()[::-1]
    if (meta.get('ElementNumberOfChannels') or 1) > 1:
        shape = np.r_[shape, meta['ElementNumberOfChannels']]
    element_size = np.dtype(meta['ElementType']).itemsize
    if memmap:
        if meta.get('BinaryDataByteOrderMSB') or meta.get('ElementByteOrderMSB'):
            raise ValueError('ByteOrderMSB is not supported with memmap')
        if meta.get('CompressedData'):
            raise ValueError('CompressedData is not supported with memmap')
        if meta['HeaderSizePerSlice'] is not None:
            raise ValueError('HeaderSizePerSlice is not supported with memmap')
        if len(meta['ElementDataFile']) != 1:
            raise ValueError('Only single ElementDataFile is supported with memmap')
        if slices is not None:
            raise ValueError('Specifying slices is not supported with memmap')
        datapath = pathlib.Path(meta['ElementDataFile'][0])
        if not datapath.is_absolute():
            datapath = filepath.parent / datapath
        offset = 0
        if islocal:
            offset += meta_size
        offset += meta.get('HeaderSize') or 0
        image = np.memmap(datapath, dtype=meta['ElementType'], mode='c', offset=offset, shape=tuple(shape))
    else:
        increment = np.prod(shape[1:], dtype=np.uintp) * np.uintp(element_size)
        if slices is None:
            slices = range(shape[0])
        slices = tuple(slices)
        if np.any(np.diff(slices) <= 0):
            raise ValueError('Slices must be strictly increasing')
        if slices and (slices[0] < 0 or slices[-1] >= shape[0]):
            raise ValueError('Slices must be bounded by z dimension')
        if len(meta['ElementDataFile']) > 1:
            shape[0] = 1
        data = io.BytesIO()

        for i, datapath in enumerate(meta['ElementDataFile']):
            datapath = pathlib.Path(datapath)
            if not datapath.is_absolute():
                datapath = filepath.parent / datapath
            with datapath.open('rb') as f:
                if islocal:
                    f.seek(meta_size, 1)
                f.seek((meta.get('HeaderSize') or 0), 1)
                if meta.get('CompressedData'):
                    if meta['CompressedDataSize'] is None:
                        raise ValueError('CompressedDataSize needs to be specified when using CompressedData')
                    if meta['HeaderSizePerSlice'] is not None:
                        raise ValueError('HeaderSizePerSlice is not supported with compressed images')
                    if len(meta['ElementDataFile']) == 1 and slices != tuple(range(shape[0])):
                        raise ValueError('Specifying slices with compressed images is not supported')
                    data.write(zlib.decompress(f.read(meta['CompressedDataSize'])))
                else:
                    read, seek = np.uintp(0), np.uintp(0)
                    for j in range(shape[0]):
                        if meta['HeaderSizePerSlice'] is not None:
                            data.write(f.read(read))
                            read = np.uintp(0)
                            seek += meta['HeaderSizePerSlice']
                        if (len(meta['ElementDataFile']) == 1 and j in slices) or (len(meta['ElementDataFile']) > 1 and i in slices):
                            f.seek(seek, 1)
                            seek = np.uintp(0)
                            read += increment
                            if read > np.iinfo(np.uintp).max - increment:
                                data.write(f.read(read))
                                read = np.uintp(0)
                        else:
                            data.write(f.read(read))
                            read = np.uintp(0)
                            seek += increment
                            if seek > np.iinfo(np.uintp).max - increment:
                                f.seek(seek, 1)
                                seek = np.uintp(0)
                    data.write(f.read(read))
        if slices:
            shape[0] = len(slices)
            image = np.frombuffer(data.getbuffer(), dtype=meta['ElementType']).reshape(shape)
            if meta.get('BinaryDataByteOrderMSB') or meta.get('ElementByteOrderMSB'):
                image.byteswap(inplace=True)
        else:
            image = None

    # remove unused metadata
    meta = {x: y for x, y in meta.items() if y is not None}
    if isinstance(meta['ElementDataFile'], (tuple, list)):
        meta['ElementDataFile'] = meta['ElementDataFile'][0]

    return image, meta


def write_image(filepath, image=None, **kwargs):
    filepath = pathlib.Path(filepath)

    # initialize metadata
    meta = dict.fromkeys(MHD_TAGS, None)
    meta['ObjectType'] = 'Image'
    meta['NDims'] = 3
    meta['BinaryData'] = True
    meta['BinaryDataByteOrderMSB'] = False
    meta['ElementSpacing'] = np.ones(3)
    meta['DimSize'] = np.zeros(3, dtype=int)
    meta['ElementType'] = float
    if image is not None:
        meta['NDims'] = np.ndim(image)
        meta['ElementSpacing'] = np.ones(np.ndim(image))
        meta['DimSize'] = np.array(np.shape(image)[::-1])
        meta['ElementType'] = np.asarray(image).dtype

    # input metadata (case incensitive)
    for key, value in kwargs.items():
        try:
            key = MHD_TAGS[[x.upper() for x in MHD_TAGS].index(key.upper())]
        except ValueError:
            pass
        else:
            meta[key] = value

    # define ElementDataFile
    if meta['ElementDataFile'] is None:
        if filepath.suffix == '.mha':
            meta['ElementDataFile'] = 'LOCAL'
        else:
            meta['ElementDataFile'] = filepath.with_suffix('.zraw' if meta.get('CompressedData') else '.raw').name

    # prepare image for saving
    if image is not None:
        if meta['ElementDataFile'].upper() == 'LOCAL':
            datapaths = [str(filepath)]
            mode = 'ab'
        elif isinstance(meta['ElementDataFile'], (tuple, list)):
            datapaths = meta['ElementDataFile']
            mode = 'wb'
            if np.ndim(image) != 3 or np.shape(image)[2] != len(datapaths):
                raise ValueError('Number filenames does not match number of slices')
        else:
            datapaths = [meta['ElementDataFile']]
            mode = 'wb'
        if meta.get('CompressedData'):
            meta['CompressedDataSize'] = 0
            for i, datapath in enumerate(datapaths):
                datapath = pathlib.Path(datapath)
                if not datapath.is_absolute():
                    datapath = filepath.parent / datapath
                data = image[i] if len(datapaths) > 1 else image
                data = data.astype(meta['ElementType']).tobytes()
                data = zlib.compress(data)
                meta['CompressedDataSize'] += len(data)

    # typecast metadata to string
    meta_out = {}
    for key, value in meta.items():
        if value is None:
            continue
        elif key in ('Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality'):
            meta_out[key] = value
        elif key in ('NDims', 'ID', 'ParentID', 'CompressedData', 'CompressedDataSize', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB', 'HeaderSize', 'HeaderSizePerSlice', 'ElementMin', 'ElementMax', 'ElementNumberOfChannels'):
            meta_out[key] = str(value)
        elif key in ('Color', 'Position', 'Offset', 'Origin', 'Orientation', 'Rotation', 'TransformMatrix', 'CenterOfRotation', 'ElementSpacing', 'DimSize', 'SequenceID', 'ElementSize'):
            meta_out[key] = ' '.join(str(x) for x in np.ravel(value))
        elif key == 'ElementType':
            try:
                meta_out[key] = [x[0] for x in MHD_TYPES.items() if np.issubdtype(value, x[1])][0]
            except IndexError as exception:
                raise ValueError(f'ElementType "{value}" is not supported') from exception
        elif key == 'ElementDataFile':
            if isinstance(value, (tuple, list)):
                meta_out[key] = 'LIST'
                for i in value:
                    meta_out[key] += f'\n{i}'
            else:
                meta_out[key] = value
        else:
            raise ValueError(f'Header tag "{key}" is not recognized')

    # write metadata to file
    with filepath.open('w') as f:
        for key, value in meta_out.items():
            f.write(f'{key} = {value}\n')

    # write image to file
    if image is not None:
        for i, datapath in enumerate(datapaths):
            datapath = pathlib.Path(datapath)
            if not datapath.is_absolute():
                datapath = filepath.parent / datapath
            data = image[i] if len(datapaths) > 1 else image
            if meta.get('BinaryDataByteOrderMSB') or meta.get('ElementByteOrderMSB'):
                data.byteswap(inplace=True)
            data = data.astype(meta['ElementType']).tobytes()
            if meta.get('CompressedData'):
                data = zlib.compress(data)
            with datapath.open(mode) as f:
                f.write(data)

    # remove unused metadata
    meta = {x: y for x, y in meta.items() if y is not None}

    return meta
