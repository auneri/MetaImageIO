import inspect
import pathlib

import setuptools


def read(filename):
    filepath = pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent / filename
    with filepath.open() as f:
        return f.read()


setuptools.setup(
    name='pymetaio',
    description=read('README.md').splitlines()[2],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Ali Uneri',
    author_email='ali.uneri@jhu.edu',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'],
    packages=setuptools.find_packages(),
    install_requires=[
        'imageio>=2.9',
        'numpy>=1.20'],
    python_requires='>=3.6')
