function meta = write(filepath, image, varargin)
    image = permute(image, ndims(image):-1:1);
    meta = py.metaimageio.write(filepath, py.numpy.asarray(image), pyargs(varargin{:}));
    meta = metaimageio.py.py2mat(meta);
end
