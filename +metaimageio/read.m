function [image, meta] = read(varargin)
% READ Read MetaImage (.mha, .mhd) files.
%
%   [IMAGE, META] = READ(FILEPATH) reads IMAGE and META.
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
addOptional(parser, 'slices', missing, @isnumeric);
parse(parser, varargin{:});
filepath = char(parser.Results.filepath);
slices = parser.Results.slices;

% load header from file
meta_in = struct();
meta_size = 0;
islist = false;
islocal = false;
fid = fopen(filepath, 'rb');
assert(fid > 0, 'Failed to open "%s"', filepath);
while ~feof(fid)
    line = fgets(fid);
    meta_size = meta_size + numel(line);
    % skip empty and commented lines
    if ~ischar(line) || isempty(line) || strncmp(line,'#',1)
        continue;
    end
    i = find(line=='=', 1, 'first');
    key = strtrim(line(1:i-1));
    value = strtrim(line(i+1:end));
    % handle case variations
    i = find(strcmpi(TAGS, key));
    if ~isempty(i)
        meta_in.(TAGS{i}) = value;
    else
        meta_in.(key) = value;
    end
    % handle one-slice-per-file data formats
    if islist
        meta_in.ElementDataFile{size(meta_in.ElementDataFile, 1) + 1, 1} = strtrim(line);
    elseif strcmpi(key, 'ElementDataFile') && strcmpi(value, 'LIST')
        meta_in.ElementDataFile = {};
        islist = true;
    elseif strcmpi(key, 'ElementDataFile') && strcmpi(value, 'LOCAL')
        meta_in.ElementDataFile = {filepath};
        islocal = true;
        break
    elseif strcmpi(key, 'ElementDataFile') && contains(value, '%')
        args = strsplit(value);
        i = cellfun(@str2num, args(2:end));
        meta_in.ElementDataFile = arrayfun(@(j) sprintf(args{1}, j), i(1):i(3):i(2), 'UniformOutput', false)';
    elseif strcmpi(key, 'ElementDataFile')
        meta_in.ElementDataFile = {value};
    end
end
fclose(fid);

% typecast metadata to native types
meta = cell2struct(repmat({missing}, size(TAGS)), TAGS, 2);
for fieldname = fieldnames(meta_in)'
    key = char(fieldname);
    switch key
        case {'Comment', 'ObjectType', 'ObjectSubType', 'TransformType', 'Name', 'AnatomicalOrientation', 'Modality', 'ElementDataFile'}
            meta.(key) = meta_in.(key);
        case {'NDims', 'ID', 'ParentID', 'CompressedDataSize', 'HeaderSize', 'HeaderSizePerSlice', 'ElementNumberOfChannels', 'ElementMin', 'ElementMax'}
            meta.(key) = str2double(meta_in.(key));
        case {'CompressedData', 'BinaryData', 'BinaryDataByteOrderMSB', 'ElementByteOrderMSB'}
            meta.(key) = strcmpi(meta_in.(key), 'true');
        case {'Color', 'Position', 'Offset', 'Origin', 'CenterOfRotation', 'ElementSpacing', 'ElementSize', 'DimSize', 'SequenceID'}
            meta.(key) = str2num(meta_in.(key)); %#ok<ST2NM>
        case {'Orientation', 'Rotation', 'TransformMatrix'}
            meta.(key) = reshape(str2num(meta_in.(key)), str2double(meta_in.NDims), str2double(meta_in.NDims)); %#ok<ST2NM>
        case 'ElementType'
            switch meta_in.(key)
                case 'MET_CHAR'
                    meta.(key) = 'int8';
                case 'MET_UCHAR'
                    meta.(key) = 'uint8';
                case 'MET_SHORT'
                    meta.(key) = 'int16';
                case 'MET_USHORT'
                    meta.(key) = 'uint16';
                case 'MET_INT'
                    meta.(key) = 'int32';
                case 'MET_LONG'
                    meta.(key) = 'int32';
                case 'MET_UINT'
                    meta.(key) = 'uint32';
                case 'MET_ULONG'
                    meta.(key) = 'uint32';
                case 'MET_FLOAT'
                    meta.(key) = 'single';
                case 'MET_DOUBLE'
                    meta.(key) = 'double';
                otherwise
                    error('metaimageio:read', 'ElementType "%s" is not supported', meta_in.(key));
            end
        otherwise
            meta.(key) = meta_in.(key);
    end
end

% read image from file
if ~isempty(slices)
    shape = meta.DimSize;
    for i = 1:2
        if numel(shape) == i
            shape(i+1) = 1;
        end
    end
    if ~ismissing(meta.ElementNumberOfChannels) && meta.ElementNumberOfChannels > 1
        shape = [meta.ElementNumberOfChannels, shape];
    end
    element = cast(0, meta.ElementType); element = whos('element'); element_size = element.bytes; %#ok<NASGU>
    precision = sprintf('*%s', meta.ElementType);
    if ismissing(slices)
        slices = 1:shape(3);
    end
    assert(isequal(slices, sort(unique(slices))), 'Slices must be strictly increasing');
    assert(slices(end) <= shape(3), 'Slices must be bounded by z dimension');
    if numel(meta.ElementDataFile) > 1
        shape(3) = 1;
    end
    image = [];

    for i = 1:numel(meta.ElementDataFile)
        datapath = meta.ElementDataFile{i};
        if ~exist(datapath, 'file')
            datapath = fullfile(fileparts(filepath), datapath);
        end
        fid = fopen(datapath, 'r');
        assert(fid > 0, 'Failed to open "%s"', datapath);
        if islocal
            fseek(fid, meta_size, 'cof');
        end
        if ~ismissing(meta.HeaderSize)
            fseek(fid, meta.HeaderSize, 'cof');
        end
        if ~ismissing(meta.CompressedData) && meta.CompressedData
            assert(~ismissing(meta.CompressedDataSize), 'CompressedDataSize needs to be specified when using CompressedData');
            assert(ismissing(meta.HeaderSizePerSlice), 'HeaderSizePerSlice is not supported with compressed images');
            assert((~ismissing(meta.ElementDataFile) && numel(meta.ElementDataFile) == 1) || all(slices == 1:shape(3)), 'Specifying slices with compressed images is not supported');            
            image = fread(fid, meta.CompressedDataSize);
            image = zlib_decompress(image, meta.ElementType);
       else
            read = 0; seek = 0;
            for j = 1:shape(3)
                if ~ismissing(meta.HeaderSizePerSlice)
                    image = [image, fread(fid, read, precision)]; %#ok<AGROW>
                    read = 0;
                    seek = seek + meta.HeaderSizePerSlice;
                end
                if (numel(meta.ElementDataFile) == 1 && any(j == slices)) || (numel(meta.ElementDataFile) > 1 && any(i == slices))
                    fseek(fid, seek, 'cof');
                    seek = 0;
                    read = read + prod(shape(1:2));
                else
                    image = [image, fread(fid, read, precision)]; %#ok<AGROW>
                    read = 0;
                    seek = seek + prod(shape(1:2)) * element_size;
                end
            end
            image = [image, fread(fid, read, precision)]; %#ok<AGROW>
        end
        fclose(fid);
    end
    shape(3) = numel(slices);
    image = reshape(image, shape);
    if ~ismissing(meta.ElementNumberOfChannels) && meta.ElementNumberOfChannels > 1
        image = permute(image, [(1:meta.NDims)+1, 1]);
    end
    if (~ismissing(meta.BinaryDataByteOrderMSB) && meta.BinaryDataByteOrderMSB) || (~ismissing(meta.ElementByteOrderMSB) && meta.ElementByteOrderMSB)
        image = swapbytes(image);
    end
else
    image = missing;
end

% remove unused metadata
for fieldname = fieldnames(meta)'
    key = char(fieldname);
    if ismissing(meta.(key))
        meta = rmfield(meta, key);
    end
end
end


function output = zlib_decompress(input, type)
error(javachk('jvm'));
buffer = java.io.ByteArrayOutputStream();
inflater = java.util.zip.Inflater();
zlib = java.util.zip.InflaterOutputStream(buffer, inflater);
zlib.write(input, 0, numel(input));
zlib.close();
output = typecast(buffer.toByteArray(), type);
end
