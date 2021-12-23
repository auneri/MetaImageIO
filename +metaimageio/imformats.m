function imformats

imformats('factory');
imformats('add', struct( ...
    'ext', ["mha", "mhd"], ...
    'isa', @isfile, ...
    'info', @info, ...
    'read', @read, ...
    'write', @write, ...
    'alpha', 0, ...
    'description', 'MetaImageIO'));
imformats

end


function meta = info(filepath)
    [~, meta] = metaimageio.read(filepath, 'slices', []);
end


function [image, map] = read(filepath)
    [image, ~] = metaimageio.read(filepath);
    map = missing;
end


function write(image, ~, filepath, varargin)
    metaimageio.write(filepath, image, varargin{:});
end
