function meta = write_image(varargin)
% WRITE_IMAGE Write MetaImage (.mha, .mhd) files.
%
%   META = WRITE_IMAGE(FILEPATH, IMAGE) writes input IMAGE array to
%   FILEPATH of the header file. Image dimensions and element data type are
%   inferred from the image, and all other tags in the META use default
%   values.
%
%   META = WRITE_IMAGE(FILEPATH, IMAGE, META) optionally input a META
%   struct which can contain some or all of the header information.
%
%   META = WRITE_IMAGE(FILEPATH) writes a header file with default tags,
%   generated META struct is returned.
%
% Please refer to http://www.itk.org/Wiki/ITK/MetaIO/Documentation for
% further details on the image file format.

% https://itk.org/Wiki/ITK/MetaIO/Documentation#Reference:_Tags_of_MetaImage
TAGS = { ...
    'Comment', ...                  % MET_STRING
    'ObjectType', ...               % MET_STRING (Image)
    'ObjectSubType', ...            % MET_STRING
    'TransformType', ...            % MET_STRING (Rigid)
    'NDims', ...                    % MET_INT
    'Name', ...                     % MET_STRING
    'ID', ...                       % MET_INT
    'ParentID', ...                 % MET_INT
    'CompressedData', ...           % MET_STRING (boolean)
    'CompressedDataSize', ...       % MET_INT
    'BinaryData', ...               % MET_STRING (boolean)
    'BinaryDataByteOrderMSB', ...   % MET_STRING (boolean)
    'ElementByteOrderMSB', ...      % MET_STRING (boolean)
    'Color', ...                    % MET_FLOAT_ARRAY[4]
    'Position', ...                 % MET_FLOAT_ARRAY[NDims]
    'Offset', ...                   % == Position
    'Origin', ...                   % == Position
    'Orientation', ...              % MET_FLOAT_MATRIX[NDims][NDims]
    'Rotation', ...                 % == Orientation
    'TransformMatrix', ...          % == Orientation
    'CenterOfRotation', ...         % MET_FLOAT_ARRAY[NDims]
    'AnatomicalOrientation', ...    % MET_STRING (RAS)
    'ElementSpacing', ...           % MET_FLOAT_ARRAY[NDims]
    'DimSize', ...                  % MET_INT_ARRAY[NDims]
    'HeaderSize', ...               % MET_INT
    'HeaderSizePerSlice', ...       % MET_INT (non-standard tag for handling per slice header)
    'Modality', ...                 % MET_STRING (MET_MOD_CT)
    'SequenceID', ...               % MET_INT_ARRAY[4]
    'ElementMin', ...               % MET_FLOAT
    'ElementMax', ...               % MET_FLOAT
    'ElementNumberOfChannels', ...  % MET_INT
    'ElementSize', ...              % MET_FLOAT_ARRAY[NDims]
    'ElementType', ...              % MET_STRING (MET_UINT)
    'ElementDataFile'};             % MET_STRING

parser = inputParser;
addRequired(parser, 'filepath');
addOptional(parser, 'image', [], @isnumeric);
parser.KeepUnmatched = true;
parse(parser, varargin{:});
filepath = char(parser.Results.filepath);
image = parser.Results.image;
meta_in = parser.Unmatched;

% initialize metadata
meta = cell2struct(repmat({missing}, size(TAGS)), TAGS, 2);
meta.ObjectType = 'Image';
meta.NDims = 3;
meta.BinaryData = true;
meta.BinaryDataByteOrderMSB = false;
meta.ElementSpacing = ones(3,1);
meta.DimSize = zeros(3,1);
meta.ElementType = 'double';
if ~isempty(image)
    meta.NDims = ndims(image);
    meta.ElementSpacing = ones(ndims(image),1);
    meta.DimSize = size(image);
    meta.ElementType = class(image);
end

% input metadata (case incensitive)
for fieldname = fieldnames(meta_in)'
    key = char(fieldname);
    % handle case variations
    i = find(strcmpi(TAGS, key));
    assert(~isempty(i), 'Header tag "%s" is not recognized', key)
    meta.(TAGS{i}) = meta_in.(key);
end

% define ElementDataFile
if ismissing(meta.ElementDataFile)
    [~, name, ext] = fileparts(filepath);
    if strcmpi(ext, '.mha')
        meta.ElementDataFile = 'LOCAL';
    else
        extension = '.raw';
        if ~ismissing(meta.CompressedData) && meta.CompressedData
            extension = '.zraw';
        end
        meta.ElementDataFile = sprintf('%s%s', name, extension);
    end
end

% prepare image for saving
if ~isempty(image)
    if ~ismissing(meta.ElementNumberOfChannels) && meta.ElementNumberOfChannels > 1
        image = permute(image, [meta.NDims+1, 1:meta.NDims]);
    end
    if strcmpi(meta.ElementDataFile, 'LOCAL')
        datapaths = {filepath};
        mode = 'a';
    elseif iscell(meta.ElementDataFile)
        datapaths = meta.ElementDataFile;
        mode = 'w';
        assert(size(image,3) == numel(datapaths), 'Number filenames does not match number of slices');
    else
        datapaths = {meta.ElementDataFile};
        mode = 'w';
    end
    if ~ismissing(meta.CompressedData) && meta.CompressedData
        meta.CompressedDataSize = 0;
    end
    datas = cell(numel(datapaths),1);
    for i = 1:numel(datapaths)
        if numel(datapaths) > 1
            data = image(:,:,i);
        else
            data = image;
        end
        if (~ismissing(meta.BinaryDataByteOrderMSB) && meta.BinaryDataByteOrderMSB) || (~ismissing(meta.ElementByteOrderMSB) && meta.ElementByteOrderMSB)
            data = swapbytes(data);
        end
        if ~ismissing(meta.CompressedData) && meta.CompressedData
            data = zlib_compress(data);
            meta.CompressedDataSize = meta.CompressedDataSize + numel(data);
            type = 'uint8';
        else
            type = meta.ElementType;
        end
        datas{i} = data(:);
    end
end

% typecast metadata to string
meta_out = struct();
for name = fieldnames(meta)'
    key = char(name);
    if ismissing(meta.(key))
        continue;
    end
    switch key
        case {'Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality'}
            meta_out.(key) = meta.(key);
        case {'NDims', 'ID', 'ParentID', 'CompressedDataSize', 'HeaderSize', 'HeaderSizePerSlice', 'ElementNumberOfChannels'}
            meta_out.(key) = sprintf('%i', meta.(key));
        case {'CompressedData', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB'}
            if meta.(key); meta_out.(key) = 'True'; else; meta_out.(key) = 'False'; end
        case {'Color', 'Position', 'Offset', 'Origin', 'CenterOfRotation', 'ElementSpacing', 'ElementSize'}
            meta_out.(key) = strtrim(sprintf('%g ', meta.(key)));
        case {'Orientation', 'Rotation', 'TransformMatrix'}
            meta_out.(key) = strtrim(sprintf('%g ', meta.(key)(:)));
        case {'DimSize', 'SequenceID'}
            meta_out.(key) = strtrim(sprintf('%i ', meta.(key)));
        case {'ElementMin', 'ElementMax'}
            meta_out.(key) = sprintf('%g', meta.(key));
        case 'ElementType'
            switch meta.(key)
                case 'int8'
                    meta_out.(key) = 'MET_CHAR';
                case 'uint8'
                    meta_out.(key) = 'MET_UCHAR';
                case 'int16'
                    meta_out.(key) = 'MET_SHORT';
                case 'uint16'
                    meta_out.(key) = 'MET_USHORT';
                case 'int32'
                    meta_out.(key) = 'MET_INT';
                case 'uint32'
                    meta_out.(key) = 'MET_UINT';
                case 'single'
                    meta_out.(key) = 'MET_FLOAT';
                case 'double'
                    meta_out.(key) = 'MET_DOUBLE';
                otherwise
                    error('pymetaio:write_image', 'ElementType "%s" is not supported', meta.(key));
            end
        case {'ElementDataFile'}
            if iscell(meta.(key))
                LIST = 'LIST';
                for i = 1:numel(meta.(key))
                    LIST = sprintf('%s\n%s', LIST, meta.(key){i});
                end
                meta_out.(key) = LIST;
            else
                meta_out.(key) = meta.(key);
            end
        otherwise
            error('pymetaio:write_image', 'Header tag "%s" is not recognized', key);
    end
end

% write metadata to file
fid = fopen(filepath, 'wt');
for name = fieldnames(meta_out)'
    key = char(name);
    fprintf(fid, '%s = %s\n', key, meta_out.(key));
end
fclose(fid);

% write image to file
if ~isempty(image)
    for i = 1:numel(datapaths)
        datapath = datapaths{i};
        if ~exist(datapath, 'file')
            datapath = fullfile(fileparts(filepath), datapath);
        end
        fid = fopen(datapath, mode);
        fwrite(fid, datas{i}, type);
        fclose(fid);
    end
end

% remove unused metadata
for fieldname = fieldnames(meta)'
    key = char(fieldname);
    if ismissing(meta.(key))
        meta = rmfield(meta, key);
    end
end
end


function output = zlib_compress(input)
error(javachk('jvm'));
input = typecast(input(:), 'uint8');
buffer = java.io.ByteArrayOutputStream();
deflater = java.util.zip.Deflater(2);
zlib = java.util.zip.DeflaterOutputStream(buffer, deflater);
zlib.write(input, 0, numel(input));
zlib.close()
output = typecast(buffer.toByteArray(), 'uint8')';
end
