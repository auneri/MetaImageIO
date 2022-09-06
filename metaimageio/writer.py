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


def write(filepath, image=None, **kwargs):
    filepath = pathlib.Path(filepath)

    # initialize metadata
    meta = dict.fromkeys(TAGS, None)
    meta['ObjectType'] = 'Image'
    meta['NDims'] = 3
    meta['BinaryData'] = True
    meta['BinaryDataByteOrderMSB'] = False
    meta['ElementSpacing'] = np.ones(3)
    meta['DimSize'] = np.zeros(3, dtype=int)
    meta['ElementType'] = float
    if image is not None:
        image = np.asarray(image)
        meta['NDims'] = np.ndim(image)
        meta['ElementSpacing'] = np.ones(np.ndim(image))
        meta['DimSize'] = np.array(np.shape(image)[::-1])
        meta['ElementType'] = np.asarray(image).dtype

    # input metadata (case incensitive)
    for key, value in kwargs.items():
        try:
            key = TAGS[[x.upper() for x in TAGS].index(key.upper())]
        except ValueError:
            pass
        meta[key] = value

    # define ElementDataFile
    if meta['ElementDataFile'] is None:
        if filepath.suffix == '.mha':
            meta['ElementDataFile'] = 'LOCAL'
        else:
            meta['ElementDataFile'] = filepath.with_suffix('.zraw' if meta.get('CompressedData') else '.raw').name

    # handle ElementNumberOfChannels
    if meta['ElementNumberOfChannels'] is not None and meta['ElementNumberOfChannels'] > 1:
        meta['DimSize'] = meta['DimSize'][:-1]
        meta['NDims'] -= 1

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
        datas = []
        for i, _ in enumerate(datapaths):
            data = image[i] if len(datapaths) > 1 else image
            if meta.get('BinaryDataByteOrderMSB') or meta.get('ElementByteOrderMSB'):
                data.byteswap(inplace=True)
            data = data.astype(meta['ElementType']).tobytes()
            if meta.get('CompressedData'):
                data = zlib.compress(data, level=2)
                meta['CompressedDataSize'] += len(data)
            datas.append(data)

    # typecast metadata to string
    meta_out = {}
    for key, value in meta.items():
        if value is None:
            continue
        elif key in ('Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality'):
            meta_out[key] = value
        elif key in ('NDims', 'ID', 'ParentID', 'CompressedData', 'CompressedDataSize', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB', 'HeaderSize', 'HeaderSizePerSlice', 'ElementMin', 'ElementMax', 'ElementNumberOfChannels'):
            meta_out[key] = str(value)
        elif key in ('Color', 'Position', 'Offset', 'Origin', 'CenterOfRotation', 'ElementSpacing', 'DimSize', 'SequenceID', 'ElementSize'):
            meta_out[key] = ' '.join(str(x) for x in np.ravel(value))
        elif key in ('Orientation', 'Rotation', 'TransformMatrix'):
            meta_out[key] = ' '.join(str(x) for x in np.ravel(np.transpose(value)))
        elif key == 'ElementType':
            try:
                meta_out[key] = [x[0] for x in TYPES.items() if np.issubdtype(value, x[1])][0]
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
            meta_out[key] = value

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
            with datapath.open(mode) as f:
                f.write(datas[i])

    # remove unused metadata
    meta = {x: y for x, y in meta.items() if y is not None}

    return meta
