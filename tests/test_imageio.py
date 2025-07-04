import numpy as np
import pytest


def test_imageio_v2(filepath):
    try:
        import imageio.v2 as iio
    except ModuleNotFoundError:
        pytest.skip()
    from metaimageio.imageio import add_format
    add_format()
    rng = np.random.default_rng()
    a = (100 * rng.random((4, 3, 2)))
    iio.imwrite(filepath, a, format='MetaImageIO')
    b = iio.imread(filepath, format='MetaImageIO')
    np.testing.assert_almost_equal(b, a)
    meta = b.meta
    np.testing.assert_almost_equal(meta['DimSize'], [2, 3, 4])


def test_imageio_v3(filepath):
    try:
        import imageio.v3 as iio
    except ModuleNotFoundError:
        pytest.skip()
    from metaimageio.imageio import MetaImageIOPlugin
    rng = np.random.default_rng()
    a = (100 * rng.random((4, 3, 2)))
    iio.imwrite(filepath, a, plugin=MetaImageIOPlugin)
    b = iio.imread(filepath, plugin=MetaImageIOPlugin)
    np.testing.assert_almost_equal(b, a)
    meta = iio.immeta(filepath, plugin=MetaImageIOPlugin)
    np.testing.assert_almost_equal(meta['DimSize'], [2, 3, 4])
