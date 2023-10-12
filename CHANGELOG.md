# MetaImageIO Changelog

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)
and the format of this document is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## Unreleased

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.5...main) for detailed changes.

## 1.1.5 -- 2023-10-12

* Fix writing when ElementNumberOfChannels > 1.

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.4...v1.1.5) for detailed changes.

## 1.1.4 -- 2023-03-09

* Fix broken package.
* Reduce minimum required imageio version.

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.3...v1.1.4) for detailed changes.

## 1.1.3 -- 2023-02-23

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.2...v1.1.3) for detailed changes.

* Fix use of relative paths with .mha files.

## 1.1.2 -- 2022-11-14

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.1...v1.1.2) for detailed changes.

## 1.1.1 -- 2022-10-28

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.1.0...v1.1.1) for detailed changes.

* Skip unsupported field names when reading in MATLAB.

## 1.1.0 -- 2022-09-06

See [individual commits](https://github.com/auneri/metaimageio/compare/v1.0.0...v1.1.0) for detailed changes.

* Support for `ElementNumberOfChannels`.
* Support for non-ndarray input image to `write`.
* Fixed transposed orientations; applies to `Orientation`, `Rotation`, `TransformMatrix`.
* Dropped `ElementDataFile` from returned metadata to avoid accidental overwrites.
* Modernized conda environment configuration and CI.

## 1.0.0 -- 2021-12-23

Initial release!
