import inspect
import pathlib

import setuptools


def read(filename):
    filepath = pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent / filename
    with filepath.open() as f:
        return f.read()


setuptools.setup(
    name='metaimageio',
    description='Support for reading and writing images in MetaIO file format.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://auneri.github.io/metaimageio',
    author='Ali Uneri',
    license='MIT',
    license_files=('LICENSE.md',),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'],
    packages=setuptools.find_packages(),
    install_requires=[
        'imageio>=2.16',
        'numpy>=1.19'],
    python_requires='>=3.6')
