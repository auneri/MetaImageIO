import numpy as np
from imageio import formats
from imageio.core import Format

from . import reader, writer

EXTENSIONS = '.mha', '.mhd'


class MetaImageIOFormat(Format):

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
                raise NotImplementedError('MetaImageIO does not support non-zero indices')
            image, meta = reader.read(self._filepath, **self.request.kwargs)
            if image is None:
                image = np.array(())
            return image, meta

        def _get_meta_data(self, index):
            if index != 0:
                raise NotImplementedError('MetaImageIO does not support non-zero indices')
            _, meta = reader.read(self._filepath, slices=())
            return meta

    class Writer(Format.Writer):

        def _open(self, **kwargs):
            self._filepath = self.request.get_local_filename()

        def _close(self):
            pass

        def _append_data(self, im, meta):
            meta.pop('ElementDataFile', None)
            meta.update(self.request.kwargs)
            writer.write(self._filepath, image=im, **meta)

        def set_meta_data(self, meta):
            raise NotImplementedError('MetaImageIO does not support writing meta data')


def imageio(name='MetaImageIO'):
    names = formats.get_format_names()
    if name.upper() not in names:
        formats.add_format(MetaImageIOFormat(
            name,
            'MetaImageIO',
            ' '.join(EXTENSIONS),
            'iv'))
        formats.sort(name, *names)
    return name
