function [image, meta] = read_image(filepath)
    oput = py.pymetaio.read_image(filepath);
    image = oput{1}.numeric();
    meta = oput{2}.struct();
    for fieldname = fieldnames(meta)'
        field = meta.(char(fieldname));
        if isa(field, 'py.str') || isa(field, 'py.type')
            meta.(char(fieldname)) = field.char();
        elseif isa(field, 'py.numpy.ndarray') | isa(field, 'py.numpy.int64')
            meta.(char(fieldname)) = field.numeric();
        elseif startsWith(class(field), 'py.')
            warning('pymetaio:read_image', 'Python type "%s" is not supported', class(field));
        end
    end
end
