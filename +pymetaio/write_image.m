function meta = write_image(filepath, image)
    meta = py.pymetaio.write_image(filepath, image);
    meta = meta.struct();
    for fieldname = fieldnames(meta)'
        field = meta.(char(fieldname));
        if isa(field, 'py.str') || isa(field, 'py.type')
            meta.(char(fieldname)) = field.char();
        elseif isa(field, 'py.numpy.ndarray') | isa(field, 'py.numpy.int64')
            meta.(char(fieldname)) = field.numeric();
        elseif startsWith(class(field), 'py.')
            warning('pymetaio:write_image', 'Python type "%s" is not supported', class(field));
        end
    end
end
