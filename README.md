# simple-scvi

[![Tests][badge-tests]][link-tests]
[![Documentation][badge-docs]][link-docs]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/scverse/simple-scvi/test.yaml?branch=main
[link-tests]: https://github.com/scverse/simple-scvi/actions/workflows/test.yml
[badge-docs]: https://img.shields.io/readthedocs/simple-scvi

External and simple implementation of scVI. This repository shows a minimal implementation of the [scVI](https://www.nature.com/articles/s41592-018-0229-2) model using [scvi-tools](https://scvi-tools.org) in an externally deployed package.

This package was initialized using the [cookicutter-scverse](https://github.com/scverse/cookiecutter-scverse) template. We advise all external projects to use the cookicutter template.

## Getting started

Please refer to the [documentation][link-docs]. In particular, the

-   [API documentation][link-api].

## Installation

You need to have Python 3.8 or newer installed on your system. If you don't have
Python installed, we recommend installing [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge).

There are several alternative options to install simple-scvi:

<!--
1) Install the latest release of `simple-scvi` from `PyPI <https://pypi.org/project/simple-scvi/>`_:

```bash
pip install simple-scvi
```
-->

1. Install the latest development version:

```bash
pip install git+https://github.com/adamgayoso/simple-scvi.git@main
```

## Release notes

See the [changelog][changelog].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][scverse-discourse].
If you found a bug, please use the [issue tracker][issue-tracker].

## Citation

```
@article{gayoso2022python,
  title={A Python library for probabilistic analysis of single-cell omics data},
  author={Gayoso, Adam and Lopez, Romain and Xing, Galen and Boyeau, Pierre and Valiollah Pour Amiri, Valeh and Hong, Justin and Wu, Katherine and Jayasuriya, Michael and Mehlman, Edouard and Langevin, Maxime and others},
  journal={Nature biotechnology},
  volume={40},
  number={2},
  pages={163--166},
  year={2022},
  publisher={Nature Publishing Group US New York}
}
```

[scverse-discourse]: https://discourse.scverse.org/
[issue-tracker]: https://github.com/adamgayoso/simple-scvi/issues
[changelog]: https://simple-scvi.readthedocs.io/latest/changelog.html
[link-docs]: https://simple-scvi.readthedocs.io
[link-api]: https://simple-scvi.readthedocs.io/latest/api.html

[//]: # (numfocus-fiscal-sponsor-attribution)

simple-scvi is part of the scverse® project ([website](https://scverse.org), [governance](https://scverse.org/about/roles)) and is fiscally sponsored by [NumFOCUS](https://numfocus.org/).
If you like scverse® and want to support our mission, please consider making a tax-deductible [donation](https://numfocus.org/donate-to-scverse) to help the project pay for developer time, professional services, travel, workshops, and a variety of other needs.

<div align="center">
<a href="https://numfocus.org/project/scverse">
  <img
    src="https://raw.githubusercontent.com/numfocus/templates/master/images/numfocus-logo.png"
    width="200"
  >
</a>
</div>

Copyright (c) 2025, Yosef Lab, Weizmann Institute of Sceince
