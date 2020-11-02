function header = write_image(filepath, image)
    header = py.pymetaio.write_image(filepath, image);
    header = header.struct();
    for fieldname = fieldnames(header)'
        field = header.(char(fieldname));
        if isa(field, 'py.str') || isa(field, 'py.type')
            header.(char(fieldname)) = field.char();
        elseif isa(field, 'py.numpy.ndarray') | isa(field, 'py.numpy.int64')
            header.(char(fieldname)) = field.numeric();
        elseif startsWith(class(field), 'py.')
            warning('pymetaio:write_image', 'Python type "%s" is not supported', class(field));
        end
    end
end
