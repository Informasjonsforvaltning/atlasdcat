"""Sphinx configuration."""
project = "atlasdcat"
author = "Jeff Reiffers and Stig B. Dørmænen"
copyright = f"2022, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
]
intersphinx_mapping = {
    "datacatalogtordf": ("https://datacatalogtordf.readthedocs.io/en/latest", None),
    "python": ("https://docs.python.org/3", None),
}
