function [image, header] = read_image(filepath)
    oput = py.pymetaio.read_image(filepath);
    image = oput{1}.numeric();
    header = oput{2}.struct();
    for fieldname = fieldnames(header)'
        field = header.(char(fieldname));
        if isa(field, 'py.str') || isa(field, 'py.type')
            header.(char(fieldname)) = field.char();
        elseif isa(field, 'py.numpy.ndarray') | isa(field, 'py.numpy.int64')
            header.(char(fieldname)) = field.numeric();
        elseif startsWith(class(field), 'py.')
            warning('pymetaio:read_image', 'Python type "%s" is not supported', class(field));
        end
    end
end
