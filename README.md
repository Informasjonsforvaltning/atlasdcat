# atlasdcat

![Tests](https://github.com/Informasjonsforvaltning/atlasdcat/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat/branch/main/graph/badge.svg?token=H4pXcHr8KK)](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat)
[![PyPI](https://img.shields.io/pypi/v/atlasdcat.svg)](https://pypi.org/project/atlasdcat/)
[![Read the Docs](https://readthedocs.org/projects/atlasdcat/badge/)](https://atlasdcat.readthedocs.io/)

A Python library for mapping [Apache Atlas](https://atlas.apache.org/) Glossary terms to DCAT metadata and vice versa.

Specification [the Norwegian Application Profile](https://data.norge.no/specification/dcat-ap-no) of [the DCAT standard](https://www.w3.org/TR/vocab-dcat-2/).

> **Notice**
> This library is part of the DCAT for Apache Atlas lifecycle and **not a complete solution**. The complete lifecycle contains the following actions:
>
> - Create glossary
> - Add dataset descriptions by using atlasdcat mapper (this library)
> - Assign dataset description glossary terms to entities (actual datasets)
> - Fetch glossary terms as DCAT catalog in RDF format (this library)


## Usage

### Install

```Shell
% pip install atlasdcat
```

### Getting started

#### Setup mapper

```Python
# Example...
from atlasdcat import AtlasDcatMapper, AtlasGlossaryClient
from pyapacheatlas.auth import BasicAuthentication

atlas_auth = BasicAuthentication(username="dummy", password="dummy")
atlas_client = AtlasGlossaryClient(
    endpoint_url="http://atlas", authentication=atlas_auth
)

mapper = AtlasDcatMapper(
    glossary_client=atlas_client,
    glossary_id="myglossary",
    catalog_uri="https://domain/catalog",
    catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
    catalog_title="Catalog",
    catalog_publisher="https://domain/publisher",
    dataset_uri_template="http://domain/datasets/{guid}",
    distribution_uri_template="http://domain/distributions/{guid}",
    language="nb",
)
```

#### Map glossary terms to DCAT Catalog RDF resource

```Python
try:
    mapper.fetch_glossary()
    catalog = mapper.map_glossary_to_dcat_dataset_catalog()
    print(catalog.to_rdf())
except Exception as e:
    print(f"An exception occurred: {e}")
```

#### Map DCAT Catalog RDF resource to glossary terms

```Python
catalog = Catalog()
catalog.identifier = "http://catalog-uri"
catalog.title = {"nb": "mytitle"}
catalog.publisher = "http://publisher"
catalog.language = ["nb"]
catalog.license = ""

dataset = Dataset()
dataset.title = {"nb": "Dataset"}
dataset.description = {"nb": "Dataset description"}
catalog.datasets = [dataset]

try:
    mapper.fetch_glossary()
    mapper.map_dataset_catalog_to_glossary_terms(catalog)
    mapper.save_glossary_terms()
except Exception as e:
    print(f"An exception occurred: {e}")
```

For an example of usage of this library in a simple server, see [example](./example/README.md).

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
