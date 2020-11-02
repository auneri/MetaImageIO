import inspect
import pathlib

import setuptools


def readme():
    filepath = pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent / 'README.md'
    with filepath.open() as f:
        return f.read()


def install_requires():
    filepath = pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent / 'requirements.txt'
    with filepath.open() as f:
        return f.read().splitlines()


setuptools.setup(
    name='pymetaio',
    description='',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Ali Uneri',
    maintainer='Ali Uneri',
    maintainer_email='ali.uneri@jhu.edu',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'],
    packages=setuptools.find_packages(),
    install_requires=install_requires(),
    python_requires='>=3.7')
