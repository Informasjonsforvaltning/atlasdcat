"""Test cases for the mapper module."""
import json
from typing import Any

from pyapacheatlas.auth import BasicAuthentication
from pyapacheatlas.core.glossary import GlossaryClient
import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from rdflib.namespace import Namespace


from atlasdcat import AtlasDcatMapper, Attribute, FormatError, TemporalError


def test_attribute_mapping() -> None:
    """Test if attributes are mapped correctly."""
    atlas_auth = BasicAuthentication(username="dummy", password="dummy")  # noqa: S106
    atlas_client = GlossaryClient(
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
    atlas_client = GlossaryClient(
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


def test_map_glossary_to_dcat_dataset_catalog(responses: Any) -> None:
    """It returns a RDF dataset catalog."""
    with open("tests/files/mock_glossary_detailed.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = GlossaryClient(
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
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    catalog = mapper.map_glossary_to_dcat_dataset_catalog()

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


def test_map_glossary_to_dcat_dataset_catalog_contact_details_missing(
    responses: Any,
) -> None:
    """It returns a RDF dataset catalog with no contact_point."""
    with open("tests/files/mock_glossary_contact_details_missing.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = GlossaryClient(
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
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    catalog = mapper.map_glossary_to_dcat_dataset_catalog()

    g1 = Graph().parse(data=catalog.to_rdf(), format="turtle")
    _dump_turtle(g1)

    DCAT = Namespace("http://www.w3.org/ns/dcat#")

    assert (None, DCAT.contactPoint, None) not in g1


def test_map_glossary_to_dcat_dataset_catalog_invalid_dates(
    responses: Any,
) -> None:
    """Should raise temporal error."""
    with open("tests/files/mock_glossary_invalid_date.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = GlossaryClient(
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
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    with pytest.raises(TemporalError):
        mapper.map_glossary_to_dcat_dataset_catalog()


def test_map_glossary_to_dcat_dataset_catalog_invalid_format_URI(
    responses: Any,
) -> None:
    """Should raise format error."""
    with open("tests/files/mock_glossary_detailed_invalid_format.json", "r") as file:
        glossary_detailed = json.loads(file.read())
    responses.add(
        method=responses.GET,
        url="http://atlas/glossary/myglossary/detailed",
        json=glossary_detailed,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = GlossaryClient(
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
            Attribute.THEME: "Tema",
            Attribute.TITLE: "Tittel",
        },
    )

    with pytest.raises(FormatError):
        mapper.map_glossary_to_dcat_dataset_catalog()


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
