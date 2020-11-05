# pyMetaIO

## Getting started

Install via `pip`.

```shell
pip install --extra-index-url http://istar-whitehole/pip --trusted-host istar-whitehole pymetaio
pip install git+https://git.lcsr.jhu.edu/auneri1/pymetaio.git
pip install /path/to/pymetaio
```

Read images with `.mha` and `.mhd` extension.

```python
import pymetaio as mio
image, header = mio.read_image('/path/to/image.mha')
```

Register as a plugin to `imageio`.

```python
import imageio
import pymetaio as mio
imageio.formats.add_format(mio.imageio)
image = imageio.imread('/path/to/image.mha', format='pymetaio')
```

Use in MATLAB.

```matlab
[image, header] = pymetaio.read_image('/path/to/image.mha');
```
