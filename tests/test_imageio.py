import metaimageio
import numpy as np
import pytest

pytest.importorskip('imageio')


def test_imageio_v2(filepath):
    try:
        import imageio.v2 as iio
    except ModuleNotFoundError:
        import imageio as iio
    metaimageio.imageio()
    a = (100 * np.random.random_sample((4, 3, 2)))
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
    a = (100 * np.random.random_sample((4, 3, 2)))
    iio.imwrite(filepath, a, plugin=MetaImageIOPlugin)
    b = iio.imread(filepath, plugin=MetaImageIOPlugin)
    np.testing.assert_almost_equal(b, a)
    meta = iio.immeta(filepath, plugin=MetaImageIOPlugin)
    np.testing.assert_almost_equal(meta['DimSize'], [2, 3, 4])
