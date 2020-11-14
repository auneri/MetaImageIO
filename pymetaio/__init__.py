import os as _os

from . import imageio  # noqa: F401
from .io import read_image, write_image  # noqa: F401

__version__ = f'0.1.{_os.getenv("PYMETAIO_COMMIT_COUNT", 0)}'
