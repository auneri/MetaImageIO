import numpy as np
from imageio import formats
from imageio.core import Format

from . import io

EXTENSIONS = '.mha', '.mhd'


class MetaIOFormat(Format):

    def _can_read(self, request):
        return request.mode[1] in self.modes and request.extension in EXTENSIONS

    def _can_write(self, request):
        return request.mode[1] in self.modes and request.extension in EXTENSIONS

    class Reader(Format.Reader):

        def _open(self, **kwargs):
            self._filepath = self.request.get_local_filename()

        def _close(self):
            pass

        def _get_length(self):
            return np.inf

        def _get_data(self, index, **kwargs):
            if index != 0:
                raise NotImplementedError('pyMetaIO does not support non-zero indices')
            image, meta = io.read_image(self._filepath, **self.request.kwargs)
            if image is None:
                image = np.array(())
            return image, meta

        def _get_meta_data(self, index):
            if index != 0:
                raise NotImplementedError('pyMetaIO does not support non-zero indices')
            _, meta = io.read_image(self._filepath, slices=())
            return meta

    class Writer(Format.Writer):

        def _open(self, **kwargs):
            self._filepath = self.request.get_local_filename()

        def _close(self):
            pass

        def _append_data(self, im, meta):
            meta.pop('ElementDataFile', None)
            meta.update(self.request.kwargs)
            io.write_image(self._filepath, image=im, **meta)

        def set_meta_data(self, meta):
            raise NotImplementedError('pyMetaIO does not support writing meta data')


def plugin(name='PYMETAIO'):
    if name.upper() not in formats.get_format_names():
        names = formats.get_format_names()
        formats.add_format(MetaIOFormat(
            name,
            'MetaIO',
            ' '.join(EXTENSIONS),
            'iv'))
        formats.sort(name, *names)
    return name
