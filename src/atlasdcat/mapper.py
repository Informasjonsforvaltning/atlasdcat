"""Mapper module for mapping an Atlas Glossery to DCAT rdf.

This module contains methods for mapping an Atlas Glossery to DCAT rdf
according to the
`dcat-ap-no v.2 standard <https://data.norge.no/specification/dcat-ap-no>`__

Example:
    >>> from atlasdcat import AtlasDcatMapper
    >>> from pyapacheatlas.auth import BasicAuthentication
    >>> from pyapacheatlas.core.glossary import GlossaryClient
    >>>
    >>> atlas_auth = BasicAuthentication(username="dummy", password="dummy")
    >>> atlas_client = GlossaryClient(
    >>>     endpoint_url="http://atlas", authentication=atlas_auth
    >>> )
    >>>
    >>> mapper = AtlasDcatMapper(
    >>>     glossary_client=atlas_client,
    >>>     glossary_id="myglossary",
    >>>     catalog_uri="https://example.com/catalog",
    >>>     catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
    >>>     catalog_title="Catalog",
    >>>     catalog_publisher="https://domain/publisher",
    >>>     dataset_uri_template="http://domain/datasets/{guid}",
    >>>     distribution_uri_template="http://domain/distributions/{guid}",
    >>>     language="nb",
    >>> )
    >>>
    >>> try:
    >>>     catalog = mapper.map_glossary_to_dcat_dataset_catalog()
    >>>     print(catalog.to_rdf())
    >>> except Exception as e:
    >>>     print(f"An exception occurred: {e}")
"""

from typing import Any, Dict, List, Optional

from concepttordf import Contact
from datacatalogtordf import (
    Catalog,
    Dataset,
    Distribution,
    InvalidDateError,
    InvalidDateIntervalError,
    InvalidURIError,
    Location,
    PeriodOfTime,
)
from pyapacheatlas.core.glossary import GlossaryClient

from .attribute import Attribute
from .termtype import TermType


class MappingError(Exception):
    """Exception class for mapping errors."""

    pass


class TemporalError(MappingError):
    """Exception class for temporal errors."""

    pass


class FormatError(MappingError):
    """Exception class for format errors."""

    pass


def _convert_term_type_to_attribute(term_type: TermType) -> Attribute:
    """Converts a TermType to Attribute.

    Args:
        term_type: A TermType

    Returns:
        An Attribute
    """
    if term_type == TermType.DATASET:
        return Attribute.DATASET
    else:
        return Attribute.DISTRIBUTION


def _parse_value(value: str) -> list:
    """Parses the value string and returns a list of codes.

    Example:

    value "code | description; code2 | description" is parsed to ['code', 'code2']

    Args:
        value: String value to parse

    Returns:
        List of parsed values
    """
    value_seperator = ";"
    code_and_desc_seperator = "|"

    if value == "":
        return []

    codes = map(
        lambda x: x.split(code_and_desc_seperator)[0].strip(" "),
        value.split(value_seperator),
    )

    return list(codes)


def _first_if_exists(a_list: list) -> str:
    """Returns the first item in a list. If the list is empty an empty string is returned.

    Args:
        a_list: A list

    Returns:
        First item
    """
    if len(a_list) >= 1:
        return a_list[0]

    return ""


def _get_term_attributes(term: Dict) -> Optional[Any]:
    """Returns attributes of the given term.

    Args:
        term: An Atlas glossary term

    Returns:
        Attributes
    """
    return (
        term.get("additionalAttributes")
        if "additionalAttributes" in term
        else term.get("attributes")
    )


def _map_location(locations: List[str]) -> List[Location]:
    """Map list of location of strings as list of Location RDF resource.

    Args:
        locations: List of locations

    Returns:
        Location
    """
    if len(locations) > 0:
        return list(map(lambda loc: Location(loc), locations))
    return []


def _map_period_of_time(start: str, end: str) -> PeriodOfTime:
    """Map list of locations as single Location RDF resource.

    Args:
        start: Start date
        end: End date

    Returns:
        Period of time
    """
    period = PeriodOfTime()
    period.start_date = start
    period.end_date = end
    return period


class AtlasDcatMapper:
    """Class for mapping Atlas Glossary terms to DCAT catalog."""

    def __init__(
        self,
        glossary_client: GlossaryClient,
        glossary_id: str,
        catalog_uri: str,
        catalog_language: str,
        catalog_title: str,
        catalog_publisher: str,
        dataset_uri_template: str,
        distribution_uri_template: str,
        language: str = "nb",
        attr_mapping: Optional[Dict] = None,
    ) -> None:
        """Initializes an AtlasDcatMapper.

        Args:
            glossary_client (GlossaryClient): A GlossaryClient (use pyapacheatlas)
            glossary_id (str): The Atlas glossary id
            catalog_uri (str): URI of this catalog
            catalog_language (str): Language of this catalog
            catalog_title (str): Title of this catalog
            catalog_publisher (str): Publisher of this catalog
            language (str): Content language (default 'nb')
            dataset_uri_template (str): Template for dataset URI
            distribution_uri_template (str): Template for distribution URI
            attr_mapping (Optional[Dict]): Attribute mapping
        """
        super().__init__()

        self._glossary_client = glossary_client
        self._glossary_id = glossary_id
        self._language = language
        self._catalog_uri = catalog_uri
        self._catalog_language = catalog_language
        self._catalog_title = catalog_title
        self._catalog_publisher = catalog_publisher
        self._dataset_uri_template = dataset_uri_template
        self._distribution_uri_template = distribution_uri_template
        self._attr_mapping = attr_mapping if attr_mapping is not None else {}

    def _get_attribute_name(self, attr: Attribute) -> str:
        """Return the name of the attribute based on a possible attribute mapping.

        Args:
            attr: An attribute

        Returns:
            Attribute name
        """
        return self._attr_mapping.get(attr, attr.value)

    def _get_term_type(self, term: Dict) -> TermType:
        """Determine the type of term.

        Args:
            term: An Atlas glossary term

        Returns:
            Type of term
        """
        attributes = _get_term_attributes(term)
        if attributes is not None:
            if self._get_attribute_name(Attribute.DATASET) in attributes:
                return TermType.DATASET
            if self._get_attribute_name(Attribute.DISTRIBUTION) in attributes:
                return TermType.DISTRIBUTION

        return TermType.UNKNOWN

    def _include_in_dcat(self, term: Dict, term_type: TermType) -> bool:
        """Determine if the term should be included.

        Args:
            term: An Atlas glossary term
            term_type: Term type

        Returns:
            Boolean
        """
        return self._get_first_attribute_value(
            term, term_type, Attribute.INCLUDE_IN_DCAT, False
        ).lower() in ["ja", "j", "yes", "y", "true"]

    def _get_attribute_values(
        self,
        term: Dict,
        term_type: TermType,
        attr: Attribute,
        parse_value: bool = False,
    ) -> list:
        """Returns a list of values of an attribute.

        Args:
            term: An Atlas glossary term
            term_type: Term type
            attr: Attribute
            parse_value: If value should be parsed, default is False

        Returns:
            List of string values
        """
        type_attribute = _convert_term_type_to_attribute(term_type)
        attributes = _get_term_attributes(term)
        if attributes is not None:
            type_attributes: Optional[Any] = attributes.get(
                self._get_attribute_name(type_attribute)
            )
            if type_attributes is not None:
                value = type_attributes.get(self._get_attribute_name(attr))
                if value is not None:
                    if parse_value and value is not None:
                        return _parse_value(value)
                    else:
                        return [value]
        return []

    def _get_first_attribute_value(
        self,
        term: Dict,
        term_type: TermType,
        attr: Attribute,
        parse_value: bool = False,
    ) -> str:
        """Returns first value of an attribute.

        Args:
            term: An Atlas glossary term
            term_type: Term type
            attr: Attribute
            parse_value: If value should be parsed, default is False

        Returns:
            Value as string
        """
        return _first_if_exists(
            self._get_attribute_values(term, term_type, attr, parse_value)
        )

    def _map_keywords(self, keywords: List) -> Optional[Dict]:
        """Maps list of keywords to RDF literal.

        Args:
            keywords: A list of keywords

        Returns:
            An keywords RDF literal
        """
        if len(keywords) > 0:
            return {self._language: ",".join(keywords)}
        return None

    def _map_contact(self, name: str, email: str) -> Optional[Contact]:
        """Maps name and email to contact RDF resource.

        Args:
            name: Contact name
            email: Contact email

        Returns:
            Contact
        """
        if len(name) > 0 or len(email) > 0:
            contact = Contact()
            contact.name = {self._language: name}
            contact.email = email
            return contact
        return None

    def _map_term_to_dataset(
        self, term: Dict, distribution_terms: List[Dict]
    ) -> Dataset:
        """Maps a glossary term of type Dataset to dataset RDF resource.

        Args:
            term: An Atlas glossary term
            distribution_terms: A list of distribution terms which will be
                mapped to this dataset based on related terms.

        Returns:
            A dataset RDF resource.

        Raises:
            TemporalError: If mapping to temporal fails
        """
        dataset = Dataset()
        # Map attributes
        dataset.identifier = self._dataset_uri_template.format(guid=term.get("guid"))
        dataset.title = {
            self._language: self._get_first_attribute_value(
                term, TermType.DATASET, Attribute.TITLE
            )
        }
        dataset.description = {self._language: term.get("longDescription")}
        dataset.frequency = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.FREQUENCY, True
        )
        dataset.publisher = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.PUBLISHER, True
        )
        dataset.theme = self._get_attribute_values(
            term, TermType.DATASET, Attribute.THEME, True
        )
        dataset.access_rights = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.ACCESS_RIGHTS, True
        )
        dataset.keyword = self._map_keywords(
            self._get_attribute_values(term, TermType.DATASET, Attribute.KEYWORD, True)
        )
        dataset.spatial = _map_location(
            self._get_attribute_values(term, TermType.DATASET, Attribute.SPATIAL, True)
        )
        dataset.spatial_resolution_in_meters = self._get_attribute_values(
            term, TermType.DATASET, Attribute.SPATIAL_RESOLUTION_IN_METERS, True
        )

        start_date = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.TEMPORAL_START_DATE
        )
        end_date = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.TEMPORAL_END_DATE
        )
        if start_date or end_date:
            try:
                temporal = _map_period_of_time(start_date, end_date)
                dataset.temporal = [temporal]
            except (InvalidDateError, InvalidDateIntervalError) as error:
                raise TemporalError(error) from error

        dataset.temporal_resolution = self._get_attribute_values(
            term, TermType.DATASET, Attribute.TEMPORAL_RESOLUTION, True
        )
        contact_point = self._map_contact(
            self._get_first_attribute_value(
                term, TermType.DATASET, Attribute.CONTACT_NAME
            ),
            self._get_first_attribute_value(
                term, TermType.DATASET, Attribute.CONTACT_EMAIL
            ),
        )
        if contact_point is not None:
            dataset.contactpoint = contact_point
        dataset.license = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.LICENSE, True
        )

        # Map related terms (distributions)
        distribution_terms_as_dict = dict(
            map(lambda t: (t.get("guid"), t), distribution_terms)
        )

        for related_term in term.get("seeAlso", []):
            if related_term.get("termGuid") in distribution_terms_as_dict:
                dataset.distributions.append(
                    self._map_term_to_distribution(
                        distribution_terms_as_dict[related_term.get("termGuid")]
                    )
                )

        return dataset

    def _map_term_to_distribution(self, term: Dict) -> Distribution:
        """Map glossary term to dcat distribution.

        Args:
            term: An Atlas glossary term.

        Returns:
            A distribution RDF resource.

        Raises:
            FormatError: If mapping to format fails
        """
        distribution = Distribution()
        distribution.identifier = self._distribution_uri_template.format(
            guid=term.get("guid")
        )
        distribution.title = {
            self._language: self._get_first_attribute_value(
                term, TermType.DISTRIBUTION, Attribute.TITLE
            )
        }
        distribution.description = {self._language: term.get("longDescription")}
        try:
            distribution.formats = self._get_attribute_values(
                term, TermType.DISTRIBUTION, Attribute.FORMAT, True
            )
        except InvalidURIError as error:
            raise FormatError(error) from error

        distribution.access_URL = self._get_first_attribute_value(
            term, TermType.DISTRIBUTION, Attribute.ACCESS_URL, True
        )
        distribution.download_URL = self._get_first_attribute_value(
            term, TermType.DISTRIBUTION, Attribute.DOWNLOAD_URL, True
        )
        distribution.license = self._get_first_attribute_value(
            term, TermType.DISTRIBUTION, Attribute.LICENSE, True
        )
        distribution.temporal_resolution = self._get_first_attribute_value(
            term, TermType.DATASET, Attribute.TEMPORAL_RESOLUTION
        )

        return distribution

    def map_glossary_to_dcat_dataset_catalog(self) -> Catalog:
        """Map glossary to dcat dataset catalog RDF resource.

        Returns:
            A catalog RDF resource.
        """
        catalog = Catalog()
        catalog.identifier = self._catalog_uri
        catalog.title = {self._language: self._catalog_title}
        catalog.publisher = self._catalog_publisher
        catalog.language = [self._catalog_language]
        catalog.license = ""

        # Fetch detailed glossary
        glossary = self._glossary_client.get_glossary(
            guid=self._glossary_id, detailed=True
        )

        dataset_terms = []
        distribution_terms = []

        # Separate terms based on type
        for (_, term) in glossary.get("termInfo", []).items():
            term_type = self._get_term_type(term)
            if term_type == TermType.DATASET and self._include_in_dcat(
                term, TermType.DATASET
            ):
                dataset_terms.append(term)
            if term_type == TermType.DISTRIBUTION and self._include_in_dcat(
                term, TermType.DISTRIBUTION
            ):
                distribution_terms.append(term)

        # Map terms to datasets
        for term in dataset_terms:
            catalog.datasets.append(self._map_term_to_dataset(term, distribution_terms))

        return catalog
