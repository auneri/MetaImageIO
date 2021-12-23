# MetaImageIO

Support for reading and writing images in [MetaIO](http://www.itk.org/Wiki/ITK/MetaIO/Documentation) file format.

[![pypi](https://img.shields.io/pypi/v/metaimageio.svg)](https://pypi.org/project/metaimageio)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/metaimageio.svg)](https://anaconda.org/conda-forge/metaimageio)
[![license](https://img.shields.io/github/license/auneri/metaimageio.svg)](https://github.com/auneri/metaimageio/blob/main/LICENSE.md)
[![build](https://img.shields.io/github/workflow/status/auneri/metaimageio/metaimageio)](https://github.com/auneri/metaimageio/actions)

## Getting started

Install using `pip install metaimageio` or `conda install -c conda-forge metaimageio`.

### Use in Python

```python
import metaimageio
image, meta = metaimageio.read('/path/to/input.mha')
metaimageio.write('/path/to/output.mha', image, ElementSpacing=meta['ElementSpacing'])
```

Add to [imageio](https://github.com/imageio/imageio) plugins.

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
