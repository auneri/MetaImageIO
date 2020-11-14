import contextlib
import pathlib
import tempfile

import numpy as np
import pymetaio as mio
import pytest

DTYPE = np.byte, np.ubyte, np.short, np.ushort, np.int, np.uint, np.single, np.double
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
        mio.write_image(f, a, CompressedData=True)
        b, _ = mio.read_image(f)
        np.testing.assert_almost_equal(b, a)


@pytest.mark.parametrize('suffix', SUFFIX)
@pytest.mark.parametrize('dtype', DTYPE)
def test_io(suffix, dtype):
    with file_with_suffix(suffix) as f:
        a = (100 * np.random.random_sample((2, 3, 4))).astype(dtype)
        mio.write_image(f, a)
        b, _ = mio.read_image(f)
        np.testing.assert_almost_equal(b, a)


@pytest.mark.parametrize('dtype', DTYPE)
def test_memmap(dtype):
    with file_with_suffix('.mhd') as f:
        a = (100 * np.random.random_sample((2, 3, 4))).astype(dtype)
        mio.write_image(f, a)
        b, _ = mio.read_image(f, memmap=True)
        np.testing.assert_almost_equal(b, a)
        del b


def test_meta():
    with file_with_suffix('.mhd') as f:
        a = np.random.random_sample((2, 3, 4))
        mio.write_image(f, a)
        b, _ = mio.read_image(f, slices=())
        assert b is None
