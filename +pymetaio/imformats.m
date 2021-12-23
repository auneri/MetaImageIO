function imformats

imformats('factory');
imformats('add', struct( ...
    'ext', ["mha", "mhd"], ...
    'isa', @isfile, ...
    'info', @info, ...
    'read', @read, ...
    'write', @write, ...
    'alpha', 0, ...
    'description', 'MetaIO'));
imformats

end


function meta = info(filepath)
    [~, meta] = pymetaio.read_image(filepath, 'slices', []);
end


function [image, map] = read(filepath)
    [image, ~] = pymetaio.read_image(filepath);
    map = missing;
end


function write(image, ~, filepath, varargin)
    pymetaio.write_image(filepath, image, varargin{:});
end
