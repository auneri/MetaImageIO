# pyMetaIO

Python implementation of the [MetaIO](http://www.itk.org/Wiki/ITK/MetaIO/Documentation) file format.

## Getting started

Install via [`conda`](https://docs.conda.io/projects/conda) (recommended)...

```shell
conda install -c http://istar-whitehole/conda pymetaio
```

... or via [`pip`](https://pip.pypa.io).

```shell
pip install --extra-index-url http://istar-whitehole/pip --trusted-host istar-whitehole pymetaio
pip install git+https://git.lcsr.jhu.edu/auneri1/pymetaio.git
pip install /path/to/pymetaio
```

Use as a plugin to [`imageio`](https://github.com/imageio/imageio) (recommended).

```python
import imageio
import pymetaio
pymetaio.imageio.plugin()
image = imageio.imread('/path/to/image.mha')
```

Read images with `.mha` and `.mhd` extension.

```python
import pymetaio
image, meta = pymetaio.read_image('/path/to/image.mha')
```

Read images in MATLAB.

```matlab
addpath(fileparts(fileparts(py.importlib.find_loader('pymetaio').path.char)));
[image, meta] = pymetaio.read_image('/path/to/image.mha');
```
