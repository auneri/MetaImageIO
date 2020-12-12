function [image, meta] = read_image(filepath)
    oput = py.pymetaio.read_image(filepath);
    image = oput{1}.numeric();
    image = permute(image, ndims(image):-1:1);
    meta = pymetaio.py2mat(oput{2});
end
