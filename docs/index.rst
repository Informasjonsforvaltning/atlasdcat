Apache Atlas DCAT library
==============================

.. toctree::
   :hidden:
   :maxdepth: 1

   modules
   atlasdcat
   example.md
   license

A Python library for mapping `Apache Atlas <https://atlas.apache.org/>`_ Glossary terms to DCAT metadata and vice versa.

Specifications `the Norwegian Application Profile <https://data.norge.no/specification/dcat-ap-no>`_ of `the DCAT standard <https://www.w3.org/TR/vocab-dcat-2/>`_.


Installation
------------

To install the datacatalogtordf package,
run this command in your terminal:

.. code-block:: console

   $ pip install atlasdcat


Usage
-----

Setup Atlas DCAT Mapper:

.. code-block::

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

Map Apache Atlas Glossary terms to DCAT RDF (turtle):

.. code-block::

    try:
        mapper.fetch_glossary()
        catalog = mapper.map_glossary_terms_to_dataset_catalog()
        print(catalog.to_rdf())
    except Exception as e:
        print(f"An exception occurred: {e}")

Map DCAT RDF Catalog to Apache Atlas Glossary terms:

.. code-block::

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


For an example of usage of this library in a simple server, see :doc:`example` .
