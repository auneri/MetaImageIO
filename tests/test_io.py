import numpy as np

import metaimageio


def test_channels(filepath_mha, dimension):
    rng = np.random.default_rng()
    a = (100 * rng.random(dimension)).astype(np.uint8)
    metaimageio.write(filepath_mha, a, ElementNumberOfChannels=a.shape[-1])
    b, _ = metaimageio.read(filepath_mha)
    np.testing.assert_almost_equal(b, a)


def test_compression(filepath, dtype):
    rng = np.random.default_rng()
    a = (100 * rng.random((4, 3, 2))).astype(dtype)
    metaimageio.write(filepath, a, CompressedData=True)
    b, _ = metaimageio.read(filepath)
    np.testing.assert_almost_equal(b, a)


def test_io(filepath, dtype, dimension):
    rng = np.random.default_rng()
    a = (100 * rng.random(dimension)).astype(dtype)
    metaimageio.write(filepath, a)
    b, _ = metaimageio.read(filepath)
    np.testing.assert_almost_equal(b, a)


def test_memmap(filepath_mha, dtype):
    rng = np.random.default_rng()
    a = (100 * rng.random((4, 3, 2))).astype(dtype)
    metaimageio.write(filepath_mha, a)
    b, _ = metaimageio.read(filepath_mha, memmap=True)
    np.testing.assert_almost_equal(b, a)
    del b
