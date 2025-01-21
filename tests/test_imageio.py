import metaimageio
import numpy as np
import pytest

imageio = pytest.importorskip('imageio')

try:
    import imageio.v2 as iio
except ModuleNotFoundError:
    import imageio as iio


@pytest.fixture(scope='module')
def imageio():
    yield metaimageio.imageio()


def test_imageio(imageio, filepath):
    assert imageio == 'MetaImageIO'
    metaimageio.imageio()
    a = (100 * np.random.random_sample((4, 3, 2)))
    iio.imwrite(filepath, a, format='MetaImageIO')
    b = iio.imread(filepath, format='MetaImageIO')
    np.testing.assert_almost_equal(b, a)
