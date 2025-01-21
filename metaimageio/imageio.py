import numpy as np

from . import reader, writer

EXTENSIONS = '.mha', '.mhd'


try:
    from imageio.core.v3_plugin_api import ImageProperties, PluginV3

    class MetaImageIOPlugin(PluginV3):

        def __init__(self, request, **kwargs):
            super().__init__(request, **kwargs)
            self._filepath = request.get_local_filename()

        def read(self, index=None, **kwargs):
            if index is not None:
                kwargs.setdefault('slices', [index])
            image, _ = reader.read(self._filepath, **kwargs)
            return image

        def write(self, ndimage, **kwargs):
            writer.write(self._filepath, image=ndimage, **kwargs)

        def metadata(self, index=None, exclude_applied=True):
            _ = index, exclude_applied
            _, meta = reader.read(self._filepath, slices=())
            return meta

        def properties(self, index=None):
            _ = index
            meta = self.metadata()
            return ImageProperties(
                shape=tuple(meta['DimSize']),
                dtype=meta['ElementType'],
                n_images=None,
                is_batch=False,
                spacing=tuple(meta['ElementSpacing']))

except ModuleNotFoundError:
    pass


try:
    from imageio import core, formats

    class MetaImageIOFormat(core.Format):

        def _can_read(self, request):
            return request.mode[1] in self.modes and request.extension in EXTENSIONS

        def _can_write(self, request):
            return request.mode[1] in self.modes and request.extension in EXTENSIONS

        class Reader(core.Format.Reader):

            def _open(self, **kwargs):
                _ = kwargs
                self._filepath = self.request.get_local_filename()

            def _close(self):
                pass

            def _get_length(self):
                return np.inf

            def _get_data(self, index, **kwargs):
                _ = kwargs
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

        class Writer(core.Format.Writer):

            def _open(self, **kwargs):
                _ = kwargs
                self._filepath = self.request.get_local_filename()

            def _close(self):
                pass

            def _append_data(self, im, meta):
                meta.pop('ElementDataFile', None)
                meta.update(self.request.kwargs)
                writer.write(self._filepath, image=im, **meta)

            def set_meta_data(self, meta):
                _ = meta
                raise NotImplementedError('MetaImageIO does not support writing meta data')

    def add_format(name='MetaImageIO'):
        names = formats.get_format_names()
        if name.upper() not in names:
            formats.add_format(MetaImageIOFormat(
                name,
                'MetaImageIO',
                ' '.join(EXTENSIONS),
                'iv'))
            formats.sort(name, *names)
        return name

except ModuleNotFoundError:
    pass
