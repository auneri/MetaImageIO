function meta = write_image(filepath, image, varargin)
    image = permute(image, ndims(image):-1:1);
    meta = py.metaimageio.write_image(filepath, py.numpy.asarray(image), pyargs(varargin{:}));
    meta = metaimageio.py.py2mat(meta);
end
