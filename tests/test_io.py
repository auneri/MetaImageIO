import contextlib
import pathlib
import tempfile

import numpy as np
import pymetaio
import pytest

DTYPE = np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64, np.float32, np.float64
SUFFIX = '.mha', '.mhd'


@contextlib.contextmanager
def file_with_suffix(suffix):
    tf = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tf.close()
    filepath = pathlib.Path(tf.name)
    try:
        yield filepath
    finally:
        for s in (suffix, '.raw', '.zraw'):
            fws = filepath.with_suffix(s)
            if fws.is_file():
                fws.unlink()


@pytest.mark.parametrize('dtype', DTYPE)
def test_compression(dtype):
    with file_with_suffix('.mhd') as f:
        a = (100 * np.random.random_sample((2, 3, 4))).astype(dtype)
        pymetaio.write_image(f, a, CompressedData=True)
        b, _ = pymetaio.read_image(f)
        np.testing.assert_almost_equal(b, a)


@pytest.mark.parametrize('suffix', SUFFIX)
@pytest.mark.parametrize('dtype', DTYPE)
def test_io(suffix, dtype):
    with file_with_suffix(suffix) as f:
        a = (100 * np.random.random_sample((2, 3, 4))).astype(dtype)
        pymetaio.write_image(f, a)
        b, _ = pymetaio.read_image(f)
        np.testing.assert_almost_equal(b, a)


@pytest.mark.parametrize('dtype', DTYPE)
def test_memmap(dtype):
    with file_with_suffix('.mhd') as f:
        a = (100 * np.random.random_sample((2, 3, 4))).astype(dtype)
        pymetaio.write_image(f, a)
        b, _ = pymetaio.read_image(f, memmap=True)
        np.testing.assert_almost_equal(b, a)
        del b


def test_meta():
    with file_with_suffix('.mhd') as f:
        a = np.random.random_sample((2, 3, 4))
        pymetaio.write_image(f, a)
        b, _ = pymetaio.read_image(f, slices=())
        assert b is None
