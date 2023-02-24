import imageio.v2 as imageio
import metaimageio
import numpy as np
import pytest
from test_io import file_with_suffix, SUFFIX


@pytest.mark.parametrize('suffix', SUFFIX)
def test_imageio(suffix):
    metaimageio.imageio()
    with file_with_suffix(suffix) as f:
        a = (100 * np.random.random_sample((2, 3, 4)))
        imageio.imwrite(f, a, format='MetaImageIO')
        b = imageio.imread(f, format='MetaImageIO')
        np.testing.assert_almost_equal(b, a)
