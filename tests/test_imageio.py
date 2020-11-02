import imageio
import numpy as np
import pymetaio as mio
import pytest
from test_io import file_with_suffix, SUFFIX

imageio.formats.add_format(mio.imageio)


@pytest.mark.parametrize('suffix', SUFFIX)
def test_imageio(suffix):
    with file_with_suffix(suffix) as f:
        a = (100 * np.random.random_sample((2, 3, 4)))
        imageio.imwrite(f, a, format='pymetaio')
        b = imageio.imread(f, format='pymetaio')
        np.testing.assert_almost_equal(b, a)
