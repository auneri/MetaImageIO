import metaimageio
import numpy as np
import pytest


@pytest.fixture(scope='module')
def matlab():
    try:
        import matlab.engine
        engine = matlab.engine.start_matlab()
    except ModuleNotFoundError:
        engine = None
    yield engine
    if engine is not None:
        engine.quit()


def mat2py(x):
    return np.transpose(x, list(reversed(range(np.ndim(x)))))


def py2mat(x):
    return mat2py(x)


def test_channels(matlab, filepath_mha, dimension):
    if matlab is None:
        pytest.skip()
    a = (100 * np.random.random_sample(dimension)).astype(np.uint8)
    matlab.metaimageio.write(str(filepath_mha), py2mat(a), {'ElementNumberOfChannels': a.shape[-1]})
    b, _ = matlab.metaimageio.read(str(filepath_mha), nargout=2)
    b = mat2py(b)
    np.testing.assert_almost_equal(b, a)


def test_io(matlab, filepath_mha, dtype, dimension):
    if matlab is None or dtype in (np.int64, np.uint64):
        pytest.skip()
    a = (100 * np.random.random_sample(dimension)).astype(dtype)
    matlab.metaimageio.write(str(filepath_mha), py2mat(a))
    b, _ = matlab.metaimageio.read(str(filepath_mha), nargout=2)
    b = mat2py(b)
    np.testing.assert_almost_equal(b, a)


def test_io_from_python(matlab, filepath_mha):
    if matlab is None:
        pytest.skip()
    a = (100 * np.random.random_sample((4, 3, 2))).astype(np.uint8)
    metaimageio.write(filepath_mha, a)
    b, _ = matlab.metaimageio.read(str(filepath_mha), nargout=2)
    b = mat2py(b)
    np.testing.assert_almost_equal(b, a)


def test_io_to_python(matlab, filepath_mha):
    if matlab is None:
        pytest.skip()
    a = (100 * np.random.random_sample((4, 3, 2))).astype(np.uint8)
    matlab.metaimageio.write(str(filepath_mha), py2mat(a))
    b, _ = metaimageio.read(filepath_mha)
    np.testing.assert_almost_equal(b, a)


def test_wrapper(matlab, filepath_mha, dtype, dimension):
    if matlab is None or dtype in (np.int32, np.uint32, np.int64, np.uint64, np.float64):
        pytest.skip()
    a = (100 * np.random.random_sample(dimension)).astype(dtype)
    matlab.metaimageio.py.write(str(filepath_mha), py2mat(a))
    b, _ = matlab.metaimageio.py.read(str(filepath_mha), nargout=2)
    b = mat2py(b)
    np.testing.assert_almost_equal(b, a)
