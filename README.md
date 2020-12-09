# pyMetaIO

Python implementation of the MetaIO file format.

## Getting started

Install via `conda` (recommended)...

```shell
conda install -c http://istar-whitehole/conda pymetaio
```

... or via `pip`.

```shell
pip install --extra-index-url http://istar-whitehole/pip --trusted-host istar-whitehole pymetaio
pip install git+https://git.lcsr.jhu.edu/auneri1/pymetaio.git
pip install /path/to/pymetaio
```

Read images with `.mha` and `.mhd` extension.

```python
import pymetaio
image, meta = pymetaio.read_image('/path/to/image.mha')
```

Register as a plugin to `imageio`.

```python
import imageio
import pymetaio
pymetaio.imageio.plugin()
image = imageio.imread('/path/to/image.mha')
```

Use in MATLAB.

```matlab
[image, meta] = pymetaio.read_image('/path/to/image.mha');
```
