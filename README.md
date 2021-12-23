# MetaImageIO

Support for reading and writing images in [MetaIO](http://www.itk.org/Wiki/ITK/MetaIO/Documentation) file format.

[![license](https://img.shields.io/github/license/auneri/metaimageio.svg)](https://github.com/auneri/metaimageio/blob/main/LICENSE.md)
[![build](https://img.shields.io/github/workflow/status/auneri/metaimageio/metaimageio)](https://github.com/auneri/metaimageio/actions)

## Getting started

### Use in Python

```python
import metaimageio
image, meta = metaimageio.read('/path/to/input.mha')
metaimageio.write('/path/to/output.mha', image, ElementSpacing=meta['ElementSpacing'])
```

Add as an [`imageio`](https://github.com/imageio/imageio) plugin.

```python
import imageio
metaimageio.imageio()
image = imageio.imread('/path/to/input.mha')
meta = image.meta
```

### Use in MATLAB

```matlab
[image, meta] = metaimageio.read('/path/to/input.mha');
metaimageio.write('/path/to/output.mha', image, 'ElementSpacing', meta.ElementSpacing);
```

Add to [image file format registry](https://www.mathworks.com/help/matlab/ref/imformats.html).

```matlab
metaimageio.imformats();
image = imread('/path/to/input.mha');
meta = imfinfo('/path/to/input.mha');
```
