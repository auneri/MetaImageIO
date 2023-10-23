import metaimageio
import numpy as np


def test_channels(filepath_mha, dimension):
    a = (100 * np.random.random_sample(dimension)).astype(np.uint8)
    metaimageio.write(filepath_mha, a, ElementNumberOfChannels=a.shape[-1])
    b, _ = metaimageio.read(filepath_mha)
    np.testing.assert_almost_equal(b, a)


def test_compression(filepath, dtype):
    a = (100 * np.random.random_sample((4, 3, 2))).astype(dtype)
    metaimageio.write(filepath, a, CompressedData=True)
    b, _ = metaimageio.read(filepath)
    np.testing.assert_almost_equal(b, a)


def test_io(filepath, dtype, dimension):
    a = (100 * np.random.random_sample(dimension)).astype(dtype)
    metaimageio.write(filepath, a)
    b, _ = metaimageio.read(filepath)
    np.testing.assert_almost_equal(b, a)


def test_memmap(filepath_mha, dtype):
    a = (100 * np.random.random_sample((4, 3, 2))).astype(dtype)
    metaimageio.write(filepath_mha, a)
    b, _ = metaimageio.read(filepath_mha, memmap=True)
    np.testing.assert_almost_equal(b, a)
    del b
