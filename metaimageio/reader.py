import io
import pathlib
import zlib

import numpy as np


# https://itk.org/Wiki/ITK/MetaIO/Documentation#Reference:_Tags_of_MetaImage
TAGS = (
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

TYPES = {
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


def read(filepath, slices=None, memmap=False):
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
                key = TAGS[[x.upper() for x in TAGS].index(key.upper())]
            except ValueError:
                pass
            meta_in[key] = value
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
    meta = dict.fromkeys(TAGS, None)
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
            meta[key] = np.array(value.split(), dtype=float).reshape(3, 3).transpose()
        elif key in ('DimSize', 'SequenceID'):
            meta[key] = np.array(value.split(), dtype=int)
        elif key in ('ElementMin', 'ElementMax'):
            meta[key] = float(value)
        elif key == 'ElementType':
            try:
                meta[key] = [x[1] for x in TYPES.items() if x[0] == value.upper()][0]
            except IndexError as exception:
                raise ValueError(f'ElementType "{value}" is not supported') from exception
        else:
            meta[key] = value

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
    meta['ElementDataFile'] = None
    meta = {x: y for x, y in meta.items() if y is not None}

    return image, meta
