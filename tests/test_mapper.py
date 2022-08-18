"""Test cases for the mapper module."""
import json
from typing import Any

from datacatalogtordf import Catalog, Dataset, Distribution
from pyapacheatlas.auth import BasicAuthentication
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from rdflib.namespace import Namespace
from responses import matchers  # type: ignore

from atlasdcat import (
    AtlasDcatMapper,
    AtlasGlossaryClient,
    Attribute,
    FormatError,
    InvalidStateError,
    MappingError,
    TemporalError,
    TermType,
)


def test_attribute_mapping() -> None:
    """Test if attributes are mapped correctly."""
    atlas_auth = BasicAuthentication(username="dummy", password="dummy")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.SPATIAL_RESOLUTION_IN_METERS: "GeografiskOppløsning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
            Attribute.TEMPORAL_START_DATE: "StartPåPerioden",
            Attribute.TEMPORAL_END_DATE: "SluttPåPerioden",
            Attribute.TEMPORAL_RESOLUTION: "PeriodeOppløsning",
        },
    )

    assert mapper._get_attribute_name(Attribute.ACCESS_RIGHTS) == "Tilgangsnivå"
    assert mapper._get_attribute_name(Attribute.ACCESS_URL) == "TilgangsUrl"
    assert mapper._get_attribute_name(Attribute.CONTACT_EMAIL) == "DataeierEpost"
    assert mapper._get_attribute_name(Attribute.CONTACT_NAME) == "Dataeier"
    assert mapper._get_attribute_name(Attribute.DATASET) == "Datasett"
    assert mapper._get_attribute_name(Attribute.DISTRIBUTION) == "Distribusjon"
    assert mapper._get_attribute_name(Attribute.DOWNLOAD_URL) == "Nedlastningslenke"
    assert mapper._get_attribute_name(Attribute.FORMAT) == "Format"
    assert mapper._get_attribute_name(Attribute.FREQUENCY) == "Oppdateringsfrekvens"
    assert (
        mapper._get_attribute_name(Attribute.INCLUDE_IN_DCAT)
        == "PubliseresPåFellesDatakatalog"
    )
    assert mapper._get_attribute_name(Attribute.KEYWORD) == "Emneord"
    assert mapper._get_attribute_name(Attribute.LICENSE) == "Lisens"
    assert mapper._get_attribute_name(Attribute.PUBLISHER) == "Utgiver"
    assert mapper._get_attribute_name(Attribute.SPATIAL) == "GeografiskAvgrensning"
    assert (
        mapper._get_attribute_name(Attribute.SPATIAL_RESOLUTION_IN_METERS)
        == "GeografiskOppløsning"
    )
    assert (
        mapper._get_attribute_name(Attribute.TEMPORAL_START_DATE) == "StartPåPerioden"
    )
    assert mapper._get_attribute_name(Attribute.TEMPORAL_END_DATE) == "SluttPåPerioden"
    assert (
        mapper._get_attribute_name(Attribute.TEMPORAL_RESOLUTION) == "PeriodeOppløsning"
    )
    assert mapper._get_attribute_name(Attribute.THEME) == "Tema"
    assert mapper._get_attribute_name(Attribute.TITLE) == "Tittel"


def test_default_attribute_mapping() -> None:
    """Test if default attribute mapping are mapped correctly."""
    atlas_auth = BasicAuthentication(username="dummy", password="dummy")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
    )

    assert mapper._get_attribute_name(Attribute.ACCESS_RIGHTS) == "accessRights"
    assert mapper._get_attribute_name(Attribute.ACCESS_URL) == "accessURL"
    assert mapper._get_attribute_name(Attribute.CONTACT_EMAIL) == "contactEmail"
    assert mapper._get_attribute_name(Attribute.CONTACT_NAME) == "contactName"
    assert mapper._get_attribute_name(Attribute.DATASET) == "Dataset"
    assert mapper._get_attribute_name(Attribute.DISTRIBUTION) == "Distribution"
    assert mapper._get_attribute_name(Attribute.DOWNLOAD_URL) == "downloadURL"
    assert mapper._get_attribute_name(Attribute.FORMAT) == "format"
    assert mapper._get_attribute_name(Attribute.FREQUENCY) == "frequency"
    assert mapper._get_attribute_name(Attribute.INCLUDE_IN_DCAT) == "includeInDCAT"
    assert mapper._get_attribute_name(Attribute.KEYWORD) == "keyword"
    assert mapper._get_attribute_name(Attribute.LICENSE) == "license"
    assert mapper._get_attribute_name(Attribute.PUBLISHER) == "publisher"
    assert mapper._get_attribute_name(Attribute.SPATIAL) == "spatial"
    assert (
        mapper._get_attribute_name(Attribute.SPATIAL_RESOLUTION_IN_METERS)
        == "spatialResolutionInMeters"
    )
    assert (
        mapper._get_attribute_name(Attribute.TEMPORAL_START_DATE) == "temporalStartDate"
    )
    assert mapper._get_attribute_name(Attribute.TEMPORAL_END_DATE) == "temporalEndDate"
    assert (
        mapper._get_attribute_name(Attribute.TEMPORAL_RESOLUTION)
        == "temporalResolution"
    )
    assert mapper._get_attribute_name(Attribute.THEME) == "theme"
    assert mapper._get_attribute_name(Attribute.TITLE) == "title"


def test_map_glossary_terms_to_dataset_catalog(responses: Any) -> None:
    """It returns a RDF dataset catalog."""
    with open("tests/files/mock_glossary_detailed_response.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    mapper.fetch_glossary()
    catalog = mapper.map_glossary_terms_to_dataset_catalog()

    # Catalog properties
    assert catalog.identifier == "https://data.norge.no/catalog/1"
    assert catalog.title == {"nb": "Catalog"}
    assert (
        catalog.publisher
        == "https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789"
    )
    assert catalog.language == [
        "http://publications.europa.eu/resource/authority/language/NOB"
    ]
    assert catalog.license == ""

    # Datasets
    assert len(catalog.datasets) == 3

    dataset_to_check = catalog.datasets[2]
    assert dataset_to_check.title == {"nb": "Kunngjøringer av offentlig anskaffelser"}
    assert dataset_to_check.description == {
        "nb": "Doffin er den nasjonale kunngjøringsdatabasen for offentlige anskaffelser "
        "Doffin hjelpe oppdragsgivere med å lage og publisere kunngjøringer i samsvar med "
        "regelverket, og gjøre det enkelt for leverandører å finne relevante konkurranser "
        "i offentlig sektor."
    }
    assert dataset_to_check.contactpoint.name == {"nb": "Contact X"}
    assert dataset_to_check.contactpoint.email == "myemail@email.com"
    assert (
        dataset_to_check.spatial[0].identifier
        == "https://data.geonorge.no/administrativeEnheter/nasjon/id/173163"
    )
    assert (
        dataset_to_check.access_rights
        == "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    assert (
        dataset_to_check.frequency
        == "http://publications.europa.eu/resource/authority/frequency/MONTHLY"
    )
    assert (
        dataset_to_check.publisher
        == "https://organization-catalog.fellesdatakatalog.digdir.no/organizations/986252932"
    )
    assert dataset_to_check.theme == [
        "https://psi.norge.no/los/ord/offentlig-innkjop",
        "http://publications.europa.eu/resource/authority/data-theme/GOVE",
    ]

    assert len(dataset_to_check.distributions) > 0
    first_distribution = dataset_to_check.distributions[0]
    assert first_distribution.title == {"nb": "CSV-fil om offentlig anskaffelser"}

    g1 = Graph().parse(data=catalog.to_rdf(), format="turtle")
    g2 = Graph().parse("tests/files/catalog.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


def test_map_glossary_terms_to_dataset_catalog_contact_details_missing(
    responses: Any,
) -> None:
    """It returns a RDF dataset catalog with no contact_point."""
    with open(
        "tests/files/mock_glossary_contact_details_missing_response.json", "r"
    ) as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    mapper.fetch_glossary()
    catalog = mapper.map_glossary_terms_to_dataset_catalog()

    g1 = Graph().parse(data=catalog.to_rdf(), format="turtle")
    _dump_turtle(g1)

    DCAT = Namespace("http://www.w3.org/ns/dcat#")

    assert (None, DCAT.contactPoint, None) not in g1


def test_map_glossary_terms_to_dataset_catalog_invalid_dates(
    responses: Any,
) -> None:
    """Should raise temporal error."""
    with open("tests/files/mock_glossary_invalid_date_response.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    mapper.fetch_glossary()
    with pytest.raises(TemporalError):
        mapper.map_glossary_terms_to_dataset_catalog()


def test_map_glossary_terms_to_dataset_catalog_invalid_format_URI(
    responses: Any,
) -> None:
    """Should raise format error."""
    with open(
        "tests/files/mock_glossary_detailed_invalid_format_response.json", "r"
    ) as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    mapper.fetch_glossary()
    with pytest.raises(FormatError):
        mapper.map_glossary_terms_to_dataset_catalog()


def test_map_dataset_catalog_to_glossary_terms(
    responses: Any,
) -> None:
    """It returns a RDF dataset catalog with no contact_point."""
    with open(
        "tests/files/mock_glossary_detailed_empty_terms_response.json", "r"
    ) as f1, open(
        "tests/files/mock_glossary_term_dataset1_response.json", "r"
    ) as f2, open(
        "tests/files/mock_glossary_term_dataset2_response.json", "r"
    ) as f3, open(
        "tests/files/mock_glossary_term_distribution1_response.json", "r"
    ) as f4, open(
        "tests/files/mock_glossary_term_distribution2_response.json", "r"
    ) as f5, open(
        "tests/files/mock_glossary_term_dataset1_request.json", "r"
    ) as f6, open(
        "tests/files/mock_glossary_term_dataset2_request.json", "r"
    ) as f7, open(
        "tests/files/mock_glossary_term_distribution1_request.json", "r"
    ) as f8, open(
        "tests/files/mock_glossary_term_distribution2_request.json", "r"
    ) as f9, open(
        "tests/files/mock_glossary_detailed_persisted_response.json", "r"
    ) as f10:
        glossary_detailed_json_response = json.loads(f1.read())
        dataset1_json_response = json.loads(f2.read())
        dataset2_json_response = json.loads(f3.read())
        distribution1_json_response = json.loads(f4.read())
        distribution2_json_response = json.loads(f5.read())
        dataset1_json_request = json.loads(f6.read())
        dataset2_json_request = json.loads(f7.read())
        distribution1_json_request = json.loads(f8.read())
        distribution2_json_request = json.loads(f9.read())
        glossary_detailed_persisted_json_response = json.loads(f10.read())

    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed_json_response,
    )
    responses.add(
        method=responses.POST,
        url="http://atlas/glossary/term",
        json=dataset1_json_response,
        match=[matchers.json_params_matcher(dataset1_json_request)],
    )
    responses.add(
        method=responses.POST,
        url="http://atlas/glossary/term",
        json=dataset2_json_response,
        match=[matchers.json_params_matcher(dataset2_json_request)],
    )
    responses.add(
        method=responses.POST,
        url="http://atlas/glossary/term",
        json=distribution1_json_response,
        match=[matchers.json_params_matcher(distribution1_json_request)],
    )
    responses.add(
        method=responses.POST,
        url="http://atlas/glossary/term",
        json=distribution2_json_response,
        match=[matchers.json_params_matcher(distribution2_json_request)],
    )
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed_persisted_json_response,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    catalog = Catalog()
    catalog.identifier = "http://catalog-uri"
    catalog.title = {"nb": "mytitle"}
    catalog.publisher = "http://publisher"
    catalog.language = ["nb"]
    catalog.license = ""

    dataset1 = Dataset()
    dataset1.title = {"nb": "Dataset 1"}
    dataset1.description = {"nb": "Dataset 1 description"}

    dataset2 = Dataset()
    dataset2.title = {"nb": "Dataset 2"}
    dataset2.description = {"nb": "Dataset 2 description"}

    distribution1 = Distribution()
    distribution1.title = {"nb": "Distribution 1"}
    distribution1.description = {"nb": "Distribution 1 description"}

    distribution2 = Distribution()
    distribution2.title = {"nb": "Distribution 2"}
    distribution2.description = {"nb": "Distribution 2 description"}

    dataset1.distributions = [distribution1]
    dataset2.distributions = [distribution2]

    catalog.datasets = [dataset1, dataset2]

    mapper.fetch_glossary()
    mapper.map_dataset_catalog_to_glossary_terms(catalog)
    mapper.save_glossary_terms()

    terms = mapper.glossary_terms

    assert len(terms) == 4
    assert terms[0] == {
        "guid": "24656c6d-0479-43b3-9bda-c1c93ab09010",
        "qualifiedName": "dataset1@myglossary",
        "name": "dataset1",
        "longDescription": "Dataset 1 description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Datasett": {
                "Dataeier": "",
                "DataeierEpost": "",
                "Emneord": "",
                "GeografiskAvgrensning": "",
                "Lisens": "",
                "Oppdateringsfrekvens": "",
                "Tema": "",
                "Tilgangsnivå": "",
                "Tittel": "Dataset 1",
                "Utgiver": "",
                "spatialResolutionInMeters": "",
                "temporalEndDate": "",
                "temporalStartDate": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec",
                "displayText": "distribution1",
            }
        ],
    }
    assert terms[1] == {
        "guid": "0c664b16-f140-4195-86be-6c6145cfb017",
        "qualifiedName": "dataset2@myglossary",
        "name": "dataset2",
        "longDescription": "Dataset 2 description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Datasett": {
                "Dataeier": "",
                "DataeierEpost": "",
                "Emneord": "",
                "GeografiskAvgrensning": "",
                "Lisens": "",
                "Oppdateringsfrekvens": "",
                "Tema": "",
                "Tilgangsnivå": "",
                "Tittel": "Dataset 1",
                "Utgiver": "",
                "spatialResolutionInMeters": "",
                "temporalEndDate": "",
                "temporalStartDate": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "2c9fc2b5-6baf-4c53-beaf-317f94e66ed9",
                "displayText": "distribution2",
            }
        ],
    }
    assert terms[2] == {
        "guid": "7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Distribusjon": {
                "Format": "",
                "Lisens": "",
                "Nedlastningslenke": "",
                "TilgangsUrl": "",
                "Tittel": "Distribution 1",
                "temporalResolution": "",
            }
        },
        "longDescription": "Distribution 1 description",
        "name": "distribution1",
        "qualifiedName": "distribution1@myglossary",
        "seeAlso": [
            {
                "termGuid": "24656c6d-0479-43b3-9bda-c1c93ab09010",
                "displayText": "dataset1",
            }
        ],
    }
    assert terms[3] == {
        "guid": "2c9fc2b5-6baf-4c53-beaf-317f94e66ed9",
        "qualifiedName": "distribution2@myglossary",
        "name": "distribution2",
        "longDescription": "Distribution 2 description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Distribusjon": {
                "Format": "",
                "Lisens": "",
                "Nedlastningslenke": "",
                "TilgangsUrl": "",
                "Tittel": "Distribution 2",
                "temporalResolution": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "0c664b16-f140-4195-86be-6c6145cfb017",
                "displayText": "dataset2",
            }
        ],
    }


def test_map_dataset_catalog_to_existing_glossary_terms(
    responses: Any,
) -> None:
    """Test update of existing glossary terms."""
    with open(
        "tests/files/mock_glossary_detailed_persisted_response.json", "r"
    ) as f1, open(
        "tests/files/mock_glossary_term_dataset1_changed_response.json", "r"
    ) as f2, open(
        "tests/files/mock_glossary_term_distribution1_changed_response.json", "r"
    ) as f3, open(
        "tests/files/mock_glossary_detailed_persisted_changed_response.json", "r"
    ) as f4:
        glossary_detailed_json_response = json.loads(f1.read())
        dataset1_json_response = json.loads(f2.read())
        distribution1_json_response = json.loads(f3.read())
        glossary_detailed_changed_json_response = json.loads(f4.read())

    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed_json_response,
    )
    responses.add(
        method=responses.PUT,
        url="http://atlas/glossary/term/24656c6d-0479-43b3-9bda-c1c93ab09010",
        json=dataset1_json_response,
    )
    responses.add(
        method=responses.PUT,
        url="http://atlas/glossary/term/7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec",
        json=distribution1_json_response,
    )
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed_changed_json_response,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={
            Attribute.ACCESS_RIGHTS: "Tilgangsnivå",
            Attribute.ACCESS_URL: "TilgangsUrl",
            Attribute.CONTACT_EMAIL: "DataeierEpost",
            Attribute.CONTACT_NAME: "Dataeier",
            Attribute.DATASET: "Datasett",
            Attribute.DISTRIBUTION: "Distribusjon",
            Attribute.DOWNLOAD_URL: "Nedlastningslenke",
            Attribute.FORMAT: "Format",
            Attribute.FREQUENCY: "Oppdateringsfrekvens",
            Attribute.INCLUDE_IN_DCAT: "PubliseresPåFellesDatakatalog",
            Attribute.KEYWORD: "Emneord",
            Attribute.LICENSE: "Lisens",
            Attribute.PUBLISHER: "Utgiver",
            Attribute.SPATIAL: "GeografiskAvgrensning",
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    catalog = Catalog()
    catalog.identifier = "http://catalog-uri"
    catalog.title = {"nb": "mytitle"}
    catalog.publisher = "http://publisher"
    catalog.language = ["nb"]
    catalog.license = ""

    dataset1 = Dataset()
    dataset1.identifier = (
        "http://data.norge.no/datasets/24656c6d-0479-43b3-9bda-c1c93ab09010"
    )
    dataset1.title = {"nb": "Dataset 1 with new title"}
    dataset1.description = {"nb": "Dataset 1 with new description"}

    distribution1 = Distribution()
    distribution1.identifier = (
        "http://data.norge.no/datasets/7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec"
    )
    distribution1.title = {"nb": "Distribution 1 with new title"}
    distribution1.description = {"nb": "Distribution 1 with new description"}

    dataset1.distributions = [distribution1]
    catalog.datasets = [dataset1]

    mapper.fetch_glossary()
    assert len(mapper.tmp_glossary_terms) == 0
    mapper.map_dataset_catalog_to_glossary_terms(catalog)
    assert len(mapper.tmp_glossary_terms) == 2

    mapper.save_glossary_terms()
    terms = mapper.glossary_terms

    assert len(terms) == 4
    assert terms[0] == {
        "guid": "24656c6d-0479-43b3-9bda-c1c93ab09010",
        "qualifiedName": "dataset1@myglossary",
        "name": "dataset1",
        "longDescription": "Dataset 1 with new description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Datasett": {
                "Dataeier": "",
                "DataeierEpost": "",
                "Emneord": "",
                "GeografiskAvgrensning": "",
                "Lisens": "",
                "Oppdateringsfrekvens": "",
                "Tema": "",
                "Tilgangsnivå": "",
                "Tittel": "Dataset 1 with new title",
                "Utgiver": "",
                "spatialResolutionInMeters": "",
                "temporalEndDate": "",
                "temporalStartDate": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec",
                "displayText": "distribution1",
            }
        ],
    }
    assert terms[1] == {
        "guid": "0c664b16-f140-4195-86be-6c6145cfb017",
        "qualifiedName": "dataset2@myglossary",
        "name": "dataset2",
        "longDescription": "Dataset 2 description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Datasett": {
                "Dataeier": "",
                "DataeierEpost": "",
                "Emneord": "",
                "GeografiskAvgrensning": "",
                "Lisens": "",
                "Oppdateringsfrekvens": "",
                "Tema": "",
                "Tilgangsnivå": "",
                "Tittel": "Dataset 1",
                "Utgiver": "",
                "spatialResolutionInMeters": "",
                "temporalEndDate": "",
                "temporalStartDate": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "2c9fc2b5-6baf-4c53-beaf-317f94e66ed9",
                "displayText": "distribution2",
            }
        ],
    }
    assert terms[2] == {
        "guid": "7fc8dbe4-0706-4da2-80b8-d0f6dab8f3ec",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Distribusjon": {
                "Format": "",
                "Lisens": "",
                "Nedlastningslenke": "",
                "TilgangsUrl": "",
                "Tittel": "Distribution 1 with new title",
                "temporalResolution": "",
            }
        },
        "longDescription": "Distribution 1 with new description",
        "name": "distribution1",
        "qualifiedName": "distribution1@myglossary",
        "seeAlso": [
            {
                "termGuid": "24656c6d-0479-43b3-9bda-c1c93ab09010",
                "displayText": "dataset1",
            }
        ],
    }
    assert terms[3] == {
        "guid": "2c9fc2b5-6baf-4c53-beaf-317f94e66ed9",
        "qualifiedName": "distribution2@myglossary",
        "name": "distribution2",
        "longDescription": "Distribution 2 description",
        "anchor": {
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        "attributes": {
            "Distribusjon": {
                "Format": "",
                "Lisens": "",
                "Nedlastningslenke": "",
                "TilgangsUrl": "",
                "Tittel": "Distribution 2",
                "temporalResolution": "",
            }
        },
        "seeAlso": [
            {
                "termGuid": "0c664b16-f140-4195-86be-6c6145cfb017",
                "displayText": "dataset2",
            }
        ],
    }


def test_raising_invalid_state() -> None:
    """Test invalid state."""
    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        glossary_client=atlas_client,
        glossary_id="myglossary",
        is_purview=True,
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
        attr_mapping={},
    )

    catalog = Catalog()
    with pytest.raises(InvalidStateError):
        mapper.map_dataset_catalog_to_glossary_terms(catalog)

    with pytest.raises(InvalidStateError):
        mapper.glossary_terms

    with pytest.raises(InvalidStateError):
        mapper._generate_qualified_name("Any Value")

    with pytest.raises(InvalidStateError):
        mapper._map_term_to_dataset({}, [])

    with pytest.raises(InvalidStateError):
        mapper._map_term_to_distribution({})

    with pytest.raises(InvalidStateError):
        mapper._map_dataset_to_terms(Dataset())

    with pytest.raises(InvalidStateError):
        mapper._map_distribution_to_term(Distribution())

    with pytest.raises(InvalidStateError):
        mapper.save_glossary_terms()

    with pytest.raises(InvalidStateError):
        mapper.map_glossary_terms_to_dataset_catalog()


def test_attributes_atlas_vs_purview() -> None:
    """Test handling attributes for both Atlas and Purview."""
    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    atlas_mapper = AtlasDcatMapper(
        is_purview=False,
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
    )
    dataset_term = {}
    assert {} == atlas_mapper._init_term_attributes(dataset_term, TermType.DATASET)
    atlas_mapper._set_attribute_values(
        dataset_term, TermType.DATASET, Attribute.TITLE, "title"
    )
    atlas_mapper._set_attribute_values(
        dataset_term,
        TermType.DATASET,
        Attribute.THEME,
        "https://theme1 | theme1;https://theme2 | theme2",
    )
    assert {
        "additionalAttributes": {
            "Dataset_title": "title",
            "Dataset_theme": "https://theme1 | theme1;https://theme2 | theme2",
        }
    } == dataset_term
    assert ["title"] == atlas_mapper._get_attribute_values(
        dataset_term, TermType.DATASET, Attribute.TITLE
    )
    assert ["https://theme1", "https://theme2"] == atlas_mapper._get_attribute_values(
        dataset_term, TermType.DATASET, Attribute.THEME, True
    )
    assert TermType.DATASET == atlas_mapper._get_term_type(dataset_term)

    distribution_term = {}
    assert {} == atlas_mapper._init_term_attributes(
        distribution_term, TermType.DISTRIBUTION
    )
    atlas_mapper._set_attribute_values(
        distribution_term, TermType.DISTRIBUTION, Attribute.TITLE, "title"
    )
    assert {
        "additionalAttributes": {"Distribution_title": "title"}
    } == distribution_term
    assert ["title"] == atlas_mapper._get_attribute_values(
        distribution_term, TermType.DISTRIBUTION, Attribute.TITLE
    )
    assert TermType.DISTRIBUTION == atlas_mapper._get_term_type(distribution_term)

    purview_mapper = AtlasDcatMapper(
        is_purview=True,
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
    )
    dataset_term = {}
    assert {"Dataset": {}} == purview_mapper._init_term_attributes(
        dataset_term, TermType.DATASET
    )
    purview_mapper._set_attribute_values(
        dataset_term, TermType.DATASET, Attribute.TITLE, "title"
    )
    purview_mapper._set_attribute_values(
        dataset_term,
        TermType.DATASET,
        Attribute.THEME,
        "https://theme1 | theme1;https://theme2 | theme2",
    )
    assert {
        "attributes": {
            "Dataset": {
                "title": "title",
                "theme": "https://theme1 | theme1;https://theme2 | theme2",
            }
        }
    } == dataset_term
    assert ["title"] == purview_mapper._get_attribute_values(
        dataset_term, TermType.DATASET, Attribute.TITLE
    )
    assert ["https://theme1", "https://theme2"] == purview_mapper._get_attribute_values(
        dataset_term, TermType.DATASET, Attribute.THEME, True
    )
    assert TermType.DATASET == purview_mapper._get_term_type(dataset_term)

    distribution_term = {}
    assert {"Distribution": {}} == purview_mapper._init_term_attributes(
        distribution_term, TermType.DISTRIBUTION
    )
    purview_mapper._set_attribute_values(
        distribution_term, TermType.DISTRIBUTION, Attribute.TITLE, "title"
    )
    assert {"attributes": {"Distribution": {"title": "title"}}} == distribution_term
    assert ["title"] == purview_mapper._get_attribute_values(
        distribution_term, TermType.DISTRIBUTION, Attribute.TITLE
    )
    assert TermType.DISTRIBUTION == purview_mapper._get_term_type(distribution_term)


def test_invalid_attributes() -> None:
    """Test handling invalid attributes."""
    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        is_purview=False,
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
    )

    with pytest.raises(MappingError):
        mapper._get_attribute_values({}, TermType.DATASET, Attribute.DATASET)


def test_validation_and_invalid_identifier(responses: Any) -> None:
    """Test handling invalid identifier."""
    with open("tests/files/mock_glossary_detailed_response.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    mapper = AtlasDcatMapper(
        is_purview=False,
        glossary_client=atlas_client,
        glossary_id="myglossary",
        catalog_uri="https://data.norge.no/catalog/1",
        catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
        catalog_title="Catalog",
        catalog_publisher="https://organization-catalog.fellesdatakatalog.digdir.no/organizations/123456789",
        dataset_uri_template="http://data.norge.no/datasets/{guid}",
        distribution_uri_template="http://data.norge.no/distributions/{guid}",
        language="nb",
    )

    mapper.fetch_glossary()
    with pytest.raises(MappingError):
        dataset = Dataset(identifier="unknown")
        mapper._map_dataset_to_terms(dataset)

    with pytest.raises(MappingError):
        dataset = Dataset(identifier="unknown")
        dataset.title = {"nb": "Unknown dataset"}
        mapper._map_dataset_to_terms(dataset)

    with pytest.raises(MappingError):
        dataset = Dataset(identifier="unknown")
        dataset.title = {"nb": "Unknown dataset"}
        dataset.description = {"nb": "Unknown dataset"}
        mapper._map_dataset_to_terms(dataset)

    with pytest.raises(MappingError):
        dataset = Dataset(
            identifier="http://data.norge.no/datasets/b87714c2-31a7-4249-8b94-fa5990eae45c"
        )
        dataset.title = {"nb": "Known dataset"}
        dataset.description = {"nb": "Known dataset"}
        dataset.keyword = {"en": ["Known dataset"]}
        mapper._map_dataset_to_terms(dataset)

    with pytest.raises(MappingError):
        distribution = Distribution(
            identifier="http://data.norge.no/datasets/b87714c2-31a7-4249-8b94-fa5990eae45c"
        )
        mapper._map_distribution_to_term(distribution)

    with pytest.raises(MappingError):
        distribution = Distribution(
            identifier="http://data.norge.no/datasets/b87714c2-31a7-4249-8b94-fa5990eae45c"
        )
        distribution.title = {"nb": "Known dataset"}
        mapper._map_distribution_to_term(distribution)

    with pytest.raises(MappingError):
        catalog = Catalog()
        catalog.language = "http://invalid-language"
        mapper.map_dataset_catalog_to_glossary_terms(catalog)

    dataset = Dataset(
        identifier="http://data.norge.no/datasets/b87714c2-31a7-4249-8b94-fa5990eae45c"
    )
    dataset.title = {"nb": "Known dataset"}
    dataset.description = {"nb": "Known dataset"}
    dataset.keyword = {"nb": ["Known dataset"]}
    terms = mapper._map_dataset_to_terms(dataset)
    assert len(terms) == 1
    assert len(terms[0].keys()) == 15

    distribution = Distribution(
        identifier="http://data.norge.no/datasets/b87714c2-31a7-4249-8b94-fa5990eae45c"
    )
    distribution.title = {"nb": "Known dataset"}
    distribution.description = {"nb": "Known dataset"}
    term = mapper._map_distribution_to_term(distribution)
    assert len(term.keys()) == 15


# ---------------------------------------------------------------------- #
# Utils for displaying debug information


def _dump_diff(g1: Graph, g2: Graph) -> None:
    in_both, in_first, in_second = graph_diff(g1, g2)
    print("\nin both:")
    _dump_turtle(in_both)
    print("\nin first:")
    _dump_turtle(in_first)
    print("\nin second:")
    _dump_turtle(in_second)


def _dump_turtle(g: Graph) -> None:
    for _l in g.serialize(format="turtle").splitlines():
        if _l:
            print(_l)
