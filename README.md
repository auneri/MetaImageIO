# MetaImageIO

Support for reading and writing images in [MetaIO](https://itk.org/Wiki/ITK/MetaIO/Documentation) file format.

[![license](https://img.shields.io/github/license/auneri/MetaImageIO)](https://github.com/auneri/metaimageio/blob/main/LICENSE.md)
[![build](https://img.shields.io/github/workflow/status/auneri/MetaImageIO/CI)](https://github.com/auneri/metaimageio/actions)
[![pypi](https://img.shields.io/pypi/v/metaimageio)](https://pypi.org/project/metaimageio)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/metaimageio)](https://anaconda.org/conda-forge/metaimageio)
[![matlab-file-exchange](https://www.mathworks.com/matlabcentral/images/matlab-file-exchange.svg)](https://www.mathworks.com/matlabcentral/fileexchange/104070-metaimageio)

## Getting started in Python

Install using `pip install metaimageio` or `conda install -c conda-forge metaimageio`.

```python
import metaimageio
image, meta = metaimageio.read('/path/to/input.mha')
metaimageio.write('/path/to/output.mha', image, ElementSpacing=meta['ElementSpacing'])
```

Add to [imageio](https://imageio.readthedocs.io) plugins.

```python
import imageio.v2 as imageio
metaimageio.imageio()
image = imageio.imread('/path/to/input.mha')
meta = image.meta
```

## Getting started in MATLAB

Install using the [Add-On Manager](https://www.mathworks.com/help/matlab/matlab_env/get-add-ons.html).

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
