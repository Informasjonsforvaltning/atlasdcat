# atlasdcat

![Tests](https://github.com/Informasjonsforvaltning/atlasdcat/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat/branch/master/graph/badge.svg)](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat)
[![PyPI](https://img.shields.io/pypi/v/atlasdcat.svg)](https://pypi.org/project/atlasdcat/)
[![Read the Docs](https://readthedocs.org/projects/atlasdcat/badge/)](https://atlasdcat.readthedocs.io/)

A Python library for mapping Apache Atlas Glossary terms to DCAT metadata and vice versa.

Specification [the Norwegian Application Profile](https://data.norge.no/specification/dcat-ap-no) of [the DCAT standard](https://www.w3.org/TR/vocab-dcat-2/).

## Usage

### Install

```Shell
% pip install atlasdcat
```

### Getting started

```Python
from atlasdcat import AtlasDcatMapper, Attribute

# Example...
from atlasdcat import AtlasDcatMapper
from pyapacheatlas.auth import BasicAuthentication

atlas_auth = BasicAuthentication(username="dummy", password="dummy")
atlas_client = GlossaryClient(
    endpoint_url="http://atlas", authentication=atlas_auth
)

mapper = AtlasDcatMapper(
    glossary_client=atlas_client,
    glossary_id="myglossary",
    catalog_uri="https://domain/catalog",
    catalog_title="Catalog",
    catalog_publisher="https://domain/publisher",
    dataset_uri_template="http://domain/datasets/{guid}",
    distribution_uri_template="http://domain/distributions/{guid}",
    language="en",
)

try:
    catalog = mapper.map_glossary_to_dcat_dataset_catalog()
    print(catalog.to_rdf())
except Exception as e:
    print(f"An exception occurred: {e}")

```

## Development

### Requirements

- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- python3
- [poetry](https://python-poetry.org/)
- [nox](https://nox.thea.codes/en/stable/)

```Shell
% pip install poetry==1.1.13
% pip install nox==2022.1.7
% pip inject nox nox-poetry==1.0.0
```

### Install developer tools

```Shell
% git clone https://github.com/Informasjonsforvaltning/atlasdcat.git
% cd atlasdcat
% pyenv install 3.8.12
% pyenv install 3.9.10
% pyenv install 3.10.
% pyenv local 3.8.12 3.9.10 3.10.
% poetry install
```

### Run all sessions

```Shell
% nox
```

### Run all tests with coverage reporting

```Shell
% nox -rs tests
```

### Debugging

You can enter into [Pdb](https://docs.python.org/3/library/pdb.html) by passing `--pdb` to pytest:

```Shell
nox -rs tests -- --pdb
```

You can set breakpoints directly in code by using the function `breakpoint()`.
