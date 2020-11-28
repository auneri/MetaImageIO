function [image, meta] = read_image(filepath)
    oput = py.pymetaio.read_image(filepath);
    image = oput{1}.numeric();
    meta = oput{2}.struct();
    for fieldname = fieldnames(meta)'
        meta.(char(fieldname)) = py2mat(meta.(char(fieldname)));
    end
end


function mat = py2mat(py)
    if isa(py, 'py.dict')
        mat = py.struct();
        for fieldname = fieldnames(mat)'
            mat.(char(fieldname)) = py2mat(mat.(char(fieldname)));
        end
    elseif isa(py, 'py.int')
        mat = py.double();
    elseif isa(py, 'py.str') || isa(py, 'py.type')
        mat = py.char();
    elseif isa(py, 'py.datetime.datetime')
        mat = datetime(py.strftime("%Y-%m-%d %H:%M:%S.%f").char());
    elseif isa(py, 'py.numpy.ndarray') || isa(py, 'py.numpy.int64')
        mat = py.numeric();
    elseif startsWith(class(py), 'py.')
        warning('oarm2:read_image', 'Python type "%s" is not supported', class(py));
        mat = py;
    else
        mat = py;
    end
end
