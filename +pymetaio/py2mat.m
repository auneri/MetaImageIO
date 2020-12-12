function y = py2mat(x)
    if isa(x, 'py.array.array') || isa(x, 'py.numpy.ndarray') || isa(x, 'py.numpy.int64')
        y = x.numeric();
    elseif isa(x, 'py.datetime.datetime')
        y = datetime(x.strftime("%Y-%m-%d %H:%M:%S.%f").char());
    elseif isa(x, 'py.dict')
        y = x.struct();
        for fieldname = fieldnames(y)'
            y.(char(fieldname)) = pymetaio.py2mat(y.(char(fieldname)));
        end
    elseif isa(x, 'py.int')
        y = x.double();
    elseif isa(x, 'py.numpy.dtype')
        y = class(x.type(0).numeric());
    elseif isa(x, 'py.str')
        y = x.char();
    elseif isa(x, 'py.tuple')
        y = py.numpy.array(x).numeric();
    elseif isa(x, 'py.type')
        y = class(x(0).numeric());
    elseif startsWith(class(x), 'py.')
        warning('oarm2:read_image', 'Python type "%s" is not supported', class(x));
        y = x;
    else
        y = x;
    end
end
