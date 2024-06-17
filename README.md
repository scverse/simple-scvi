# simple-scvi

[![Tests][badge-tests]][link-tests]
[![Documentation][badge-docs]][link-docs]

External and simple implementation of scVI. This repository shows a minimal implementation of the
[scVI](https://www.nature.com/articles/s41592-018-0229-2) model using
[scvi-tools](https://scvi-tools.org) in an externally deployed package.

This package was initialized using the
[cookicutter-scverse](https://github.com/scverse/cookiecutter-scverse) template. We advise all
external projects to use the cookicutter template.

## Getting started

Please refer to the [documentation][link-docs]. In particular, the

- [API documentation][link-api].

## Installation

You need to have Python 3.9 or newer installed on your system. Install the latest development
version using pip:

```bash
pip install git+https://github.com/adamgayoso/simple-scvi.git@main
```

## Release notes

See the [changelog].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][scverse-discourse].
If you found a bug, please use the [issue tracker][issue-tracker].

## Citation

> **A Python library for probabilistic analysis of single-cell omics data**
>
> Adam Gayoso, Romain Lopez, Galen Xing, Pierre Boyeau, Valeh Valiollah Pour Amiri, Justin Hong,
> Katherine Wu, Michael Jayasuriya, Edouard Mehlman, Maxime Langevin, Yining Liu, Jules Samaran,
> Gabriel Misrachi, Achille Nazaret, Oscar Clivio, Chenling Xu, Tal Ashuach, Mariano Gabitto,
> Mohammad Lotfollahi, Valentine Svensson, Eduardo da Veiga Beltrame, Vitalii Kleshchevnikov,
> Carlos Talavera-López, Lior Pachter, Fabian J. Theis, Aaron Streets, Michael I. Jordan,
> Jeffrey Regier & Nir Yosef
>
> _Nature Biotechnology_ 2022 Feb 07. doi: [10.1038/s41587-021-01206-w](https://doi.org/10.1038/s41587-021-01206-w).

[badge-docs]: https://img.shields.io/readthedocs/simple-scvi
[badge-tests]: https://img.shields.io/github/actions/workflow/status/scverse/simple-scvi/test.yaml?branch=main
[changelog]: https://simple-scvi.readthedocs.io/latest/changelog.html
[issue-tracker]: https://github.com/adamgayoso/simple-scvi/issues
[link-api]: https://simple-scvi.readthedocs.io/latest/api.html
[link-docs]: https://simple-scvi.readthedocs.io
[link-tests]: https://github.com/scverse/simple-scvi/actions/workflows/test.yml
[scverse-discourse]: https://discourse.scverse.org/
