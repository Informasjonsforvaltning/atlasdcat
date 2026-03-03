# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

**atlasdcat** is a Python library for bidirectional mapping between Apache Atlas glossary terms and DCAT (Data Catalog Vocabulary) metadata, following the Norwegian DCAT-AP-NO v2 specification. It supports both native Apache Atlas and Azure Purview glossary formats.

## Commands

### Install dependencies

```
poetry install
```

### Run default nox sessions (lint, mypy, pytype, tests)

```
nox
```

### Run tests with coverage

```
nox -rs tests
```

### Run a single test by name

```
nox -rs tests -- -k "test_name"
```

### Run tests with debugger

```
nox -rs tests -- --pdb
```

### Lint

```
nox -rs lint
```

### Type checking

```
nox -rs mypy
```

### Format code

```
nox -rs black
```

### Security audit

```
pip audit
```

## Code Style

- Formatter: **black** (max line length 88)
- Linter: **flake8** with Google-style docstrings and import ordering
- Type checking: **mypy** (strict mode off, but warn_unreachable enabled)
- Coverage: **100% required** (enforced via `fail_under = 100`)
- Docstrings: Google convention, checked by darglint (strictness: short)

## Test Structure

Tests are in `tests/` with mock JSON data in `tests/files/`. Tests use `pytest-mock` for mocking and `pytest-responses` for HTTP mocking. The test files mirror the source modules (`test_mapper.py`, `test_atlas_client.py`).
