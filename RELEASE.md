# MetaImageIO Release Instructions

1. Create a new tag
    * update `__version__` and `CHANGELOG` with commit message "Release vX.X.X"
    * add tag with message "Release vX.X.X"
    * push changes to [metaimageio](https://github.com/auneri/metaimageio)

2. Upload new package to PyPI

    ```bash
    conda activate base
    python setup.py sdist bdist_wheel
    twine upload dist/*
    ```

3. Upload new package to conda-forge
    * make a pull request to [metaimageio-feedstock](https://github.com/conda-forge/metaimageio-feedstock)
    * update `version` (should match `__version__`) and `hash` (should match PyPI) in `recipe/meta.yaml`
