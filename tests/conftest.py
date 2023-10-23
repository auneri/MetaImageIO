import pathlib
import tempfile

import numpy as np
import pytest


@pytest.fixture(scope='module', params=((3, 2), (4, 3, 2), (5, 4, 3, 2)))
def dimension(request):
    yield request.param


@pytest.fixture(scope='module', params=(np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64, np.float32, np.float64))
def dtype(request):
    yield request.param


@pytest.fixture(scope='function')
def filepath(suffix):
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        filepath = pathlib.Path(f.name)
    yield filepath
    for s in (suffix, '.raw', '.zraw'):
        fws = filepath.with_suffix(s)
        if fws.is_file():
            fws.unlink()


@pytest.fixture(scope='function')
def filepath_mha():
    with tempfile.NamedTemporaryFile(suffix='.mha', delete=False) as f:
        filepath = pathlib.Path(f.name)
    yield filepath
    if filepath.is_file():
        filepath.unlink()


@pytest.fixture(scope='module', params=('.mha', '.mhd'))
def suffix(request):
    yield request.param
