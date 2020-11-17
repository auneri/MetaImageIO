import os
__version__ = f'0.1.{os.getenv("PYMETAIO_COMMIT_COUNT", 0)}'
