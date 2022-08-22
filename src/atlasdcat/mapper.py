"""Mapper module for mapping an Atlas Glossery to DCAT rdf.

This module contains methods for mapping an Atlas Glossery to DCAT rdf
according to the
`dcat-ap-no v.2 standard <https://data.norge.no/specification/dcat-ap-no>`__

Example:
    Setup the AtlasDcatMapper.
    >>> from atlasdcat import AtlasDcatMapper, AtlasGlossaryClient
    >>> from pyapacheatlas.auth import BasicAuthentication
    >>>
    >>> atlas_auth = BasicAuthentication(username="dummy", password="dummy")
    >>> atlas_client = AtlasGlossaryClient(
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

    Map glossary terms to DCAT Catalog
    >>> try:
    >>>     mapper.fetch_glossary()
    >>>     catalog = mapper.map_glossary_to_dcat_dataset_catalog()
    >>>     print(catalog.to_rdf())
    >>> except Exception as e:
    >>>     print(f"An exception occurred: {e}")

    >>> catalog = Catalog()
    >>> catalog.identifier = "http://catalog-uri"
    >>> catalog.title = {"nb": "mytitle"}
    >>> catalog.publisher = "http://publisher"
    >>> catalog.language = ["nb"]
    >>> catalog.license = ""

    >>> dataset = Dataset()
    >>> dataset.title = {"nb": "Dataset"}
    >>> dataset.description = {"nb": "Dataset description"}
    >>> catalog.datasets = [dataset]
    >>>
    >>> try:
    >>>  6+
     mapper.fetch_glossary()
            mapper.map_dataset_catalog_to_glossary_terms(catalog)
            mapper.save_glossary_terms()
        except Exception as e:
            print(f"An exception occurred: {e}")
"""
from typing import Any, Dict, List, Optional
import uuid

from datacatalogtordf import (
    Catalog,
    Contact,
    Dataset,
    Distribution,
    InvalidDateError,
    InvalidDateIntervalError,
    InvalidURIError,
    Location,
    PeriodOfTime,
)
from pyapacheatlas.core.glossary import (
    AtlasGlossaryTerm,
)

from .attribute import Attribute
from .glossaryclient import AtlasGlossaryClient
from .termtype import TermType

VALUE_SEPERATOR = ";"
CODE_AND_DESC_SEPERATOR = "|"


class MappingError(Exception):
    """Exception class for mapping errors."""

    pass


class TemporalError(MappingError):
    """Exception class for temporal errors."""

    pass


class FormatError(MappingError):
    """Exception class for format errors."""

    pass


class InvalidStateError(MappingError):
    """Exception class for invalid state errors."""

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
    if value == "":
        return []

    codes = map(
        lambda x: x.split(CODE_AND_DESC_SEPERATOR)[0].strip(" "),
        value.split(VALUE_SEPERATOR),
    )

    return list(codes)


def _format_value(codes: List[List]) -> str:
    return VALUE_SEPERATOR.join(CODE_AND_DESC_SEPERATOR.join(c) for c in codes)


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


def _extract_guid(template: str, value: str) -> str:
    """Extract guid from value based on template.

    Args:
        template: The template
        value: Value to extract from

    Returns:
        Guid
    """
    strings = template.split("{guid}")
    for s in strings:
        value = value.replace(s, "")

    return value


def _generate_name(value: str) -> str:
    """Generate term name.

    Args:
        value: Value to generate the name from

    Returns:
        Name
    """
    return value.replace(" ", "").lower()


class AtlasDcatMapper:
    """Class for mapping Atlas Glossary terms to DCAT catalog."""

    def __init__(
        self,
        glossary_client: AtlasGlossaryClient,
        glossary_id: str,
        catalog_uri: str,
        catalog_language: str,
        catalog_title: str,
        catalog_publisher: str,
        dataset_uri_template: str,
        distribution_uri_template: str,
        language: str = "nb",
        attr_mapping: Optional[Dict] = None,
        is_purview: Optional[bool] = None,
        include_approved_only: bool = False,
    ) -> None:
        """Initializes an AtlasDcatMapper.

        Args:
            glossary_client (AtlasGlossaryClient): An AtlasGlossaryClient
            glossary_id (str): The Atlas glossary id
            catalog_uri (str): URI of this catalog
            catalog_language (str): Language of this catalog
            catalog_title (str): Title of this catalog
            catalog_publisher (str): Publisher of this catalog
            language (str): Content language (default 'nb')
            dataset_uri_template (str): Template for dataset URI
            distribution_uri_template (str): Template for distribution URI
            attr_mapping (Optional[Dict]): Attribute mapping.
            is_purview (Optional[bool]): If the glossary endpoint is a Purview
                instance. Auto-detect by default.
            include_approved_only: If the mapper should only include terms with
                status approved (Purview only).
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
        self._is_purview = (
            is_purview is None and "purview.azure.com" in glossary_client.endpoint_url
        ) or (is_purview is not None and is_purview)
        self._include_approved_only = include_approved_only and is_purview
        self._glossary: Optional[Dict] = None
        self._tmp_glossary_terms: List = []

    @property
    def glossary_terms(self) -> List[Dict]:
        """List[Dict], the persisted glossary terms."""
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct or call one "
                "of the two mapping functions before using this property."
            )

        return [item[1] for item in self._glossary.get("termInfo", {}).items()]

    @property
    def tmp_glossary_terms(self) -> List[Dict]:
        """Dict, the temporary glossary terms."""  # noqa: B950
        return self._tmp_glossary_terms

    def _generate_qualified_name(self, value: str) -> str:
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct."
            )

        return "{name}@{glossary}".format(
            name=_generate_name(value), glossary=self._glossary.get("qualifiedName", "")
        )

    def _get_term_attributes(self, term: Dict) -> Optional[Dict]:
        """Returns attributes of the given term.

        Args:
            term: An Atlas glossary term

        Returns:
            Attributes
        """
        return (
            term.get("attributes")
            if self._is_purview
            else term.get("additionalAttributes")
        )

    def _init_term_attributes(self, term: Dict, term_type: TermType) -> Dict:
        """Initialize term attributes.

        Args:
            term: An Atlas glossary term
            term_type: A term type

        Returns:
            Attributes
        """
        type_attribute = _convert_term_type_to_attribute(term_type)
        type_attribute_name = self._get_attribute_name(type_attribute)

        if self._is_purview:
            term["attributes"] = {type_attribute_name: {}}
            return term["attributes"]
        else:
            term["additionalAttributes"] = {}
            return term["additionalAttributes"]

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
        attributes = self._get_term_attributes(term)
        if attributes is not None:
            if self._is_purview:
                if self._get_attribute_name(Attribute.DATASET) in attributes:
                    return TermType.DATASET
                if self._get_attribute_name(Attribute.DISTRIBUTION) in attributes:
                    return TermType.DISTRIBUTION
            else:
                for (name, _) in attributes.items():
                    if name.startswith(
                        self._get_attribute_name(Attribute.DATASET) + "_"
                    ):
                        return TermType.DATASET
                    if name.startswith(
                        self._get_attribute_name(Attribute.DISTRIBUTION) + "_"
                    ):
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
        ).lower() not in ["nei", "n", "no", "false"]

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

        Raises:
            MappingError: A mapping error if the attributes are undefined
        """
        attributes = self._get_term_attributes(term)

        if attributes is None:
            raise MappingError("Term attributes is undefined")

        type_attribute = _convert_term_type_to_attribute(term_type)

        if self._is_purview:
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
        else:
            attribute_name = "{prefix}_{name}".format(
                prefix=self._get_attribute_name(type_attribute),
                name=self._get_attribute_name(attr),
            )
            value = attributes.get(attribute_name)
            if value is not None:
                if parse_value and value is not None:
                    return _parse_value(value)
                else:
                    return [value]

        return []

    def _set_attribute_values(
        self, term: Dict, term_type: TermType, attr: Attribute, values: str
    ) -> None:
        """Sets the value of an attribute.

        Args:
            term: An Atlas glossary term
            term_type: Term type
            attr: Attribute
            values: Attribute values as string

        """
        attributes = self._get_term_attributes(term)

        if attributes is None:
            attributes = self._init_term_attributes(term, term_type)

        type_attribute = _convert_term_type_to_attribute(term_type)

        if self._is_purview:
            type_attributes: Optional[Any] = attributes.get(
                self._get_attribute_name(type_attribute)
            )
            if type_attributes is not None:
                type_attributes[self._get_attribute_name(attr)] = values
        else:
            attribute_name = "{prefix}_{name}".format(
                prefix=self._get_attribute_name(type_attribute),
                name=self._get_attribute_name(attr),
            )
            attributes[attribute_name] = values

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

    def _get_persisted_term(self, guid: str) -> Optional[Dict]:
        for term in self.glossary_terms:
            if term.get("guid") == guid:
                return term

        return None

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
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

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
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

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
        distribution.temporal_resolution = self._get_attribute_values(
            term, TermType.DATASET, Attribute.TEMPORAL_RESOLUTION, True
        )

        return distribution

    def _map_dataset_to_terms(self, dataset: Dataset) -> List[Dict]:
        """Maps a dataset RDF resource to glossary terms.

        Args:
            dataset: A dataset RDF resource

        Returns:
            A list with glossary terms

        Raises:
            MappingError: A mapping error if the language does not match
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

        if not (hasattr(dataset, "title") and self._language in dataset.title):
            raise MappingError(
                "Dataset title is not defined or does not match mapper language."
            )
        if not (
            hasattr(dataset, "description") and self._language in dataset.description
        ):
            raise MappingError(
                "Dataset description title is not defined or does not match mapper language."
            )
        if hasattr(dataset, "keyword") and not (self._language in dataset.keyword):
            raise MappingError("Dataset keyword does not match mapper language.")

        terms = []

        dataset_title = dataset.title.get(self._language)
        dataset_term = AtlasGlossaryTerm(
            guid="tmp-{}".format(uuid.uuid4()),
            glossaryGuid=self._glossary_id,
            name=_generate_name(dataset_title),
            qualifiedName=self._generate_qualified_name(dataset_title),
            longDescription=dataset.description.get(self._language),
        ).to_json()

        if hasattr(dataset, "identifier"):
            guid = _extract_guid(self._dataset_uri_template, dataset.identifier)
            dataset_term = self._get_persisted_term(guid)
            if dataset_term is None:
                raise MappingError(
                    "Could not find term with guid {guid}".format(guid=guid)
                )

        dataset_term["longDescription"] = dataset.description.get(self._language)

        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.TITLE,
            dataset.title[self._language],
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.PUBLISHER,
            _format_value([[dataset.publisher, ""]])
            if hasattr(dataset, "publisher")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.FREQUENCY,
            _format_value([[dataset.frequency, ""]])
            if hasattr(dataset, "frequency")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.ACCESS_RIGHTS,
            _format_value([[dataset.access_rights, ""]])
            if hasattr(dataset, "access_rights")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.THEME,
            _format_value([[item, ""] for item in dataset.theme])
            if hasattr(dataset, "theme")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.KEYWORD,
            _format_value([[item] for item in dataset.keyword.get(self._language)])
            if hasattr(dataset, "keyword")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.SPATIAL,
            _format_value([[item.identifier, ""] for item in dataset.spatial])
            if hasattr(dataset, "spatial")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.SPATIAL_RESOLUTION_IN_METERS,
            _format_value([[item] for item in dataset.spatial_resolution_in_meters])
            if hasattr(dataset, "spatial_resolution_in_meters")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.TEMPORAL_START_DATE,
            dataset.temporal[0].start_date
            if hasattr(dataset, "temporal") and len(dataset.temporal) > 0
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.TEMPORAL_END_DATE,
            dataset.temporal[0].end_date
            if hasattr(dataset, "temporal") and len(dataset.temporal) > 0
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.SPATIAL_RESOLUTION_IN_METERS,
            _format_value([[item] for item in dataset.temporal_resolution])
            if hasattr(dataset, "temporal_resolution")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.CONTACT_NAME,
            dataset.contactpoint.name[self._language]
            if hasattr(dataset, "contactpoint")
            else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.CONTACT_EMAIL,
            dataset.contactpoint.email if hasattr(dataset, "contactpoint") else "",
        )
        self._set_attribute_values(
            dataset_term,
            TermType.DATASET,
            Attribute.LICENSE,
            _format_value([[dataset.license, ""]])
            if hasattr(dataset, "license")
            else "",
        )

        terms.append(dataset_term)
        for dist in dataset.distributions:
            dist_term = self._map_distribution_to_term(dist)
            dist_term["seeAlso"].append(
                {
                    "termGuid": dataset_term.get("guid"),
                    "displayText": dataset_term.get("name"),
                }
            )

            terms.append(dist_term)

        return terms

    def _map_distribution_to_term(self, distribution: Distribution) -> Dict:
        """Maps a distribution RDF resource to glossary term.

        Args:
            distribution: A distribution RDF resource

        Returns:
            A glossary term

        Raises:
            MappingError: A mapping error if the language does not match
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

        if not (
            hasattr(distribution, "title") and self._language in distribution.title
        ):
            raise MappingError(
                "Distribution title is not defined or does not match mapper language."
            )
        if not (
            hasattr(distribution, "description")
            and self._language in distribution.description
        ):
            raise MappingError(
                "Distribution description title is not defined or does not match "
                "mapper language."
            )

        distribution_title = distribution.title.get(self._language)
        distribution_term = AtlasGlossaryTerm(
            guid="tmp-{}".format(uuid.uuid4()),
            glossaryGuid=self._glossary_id,
            name=_generate_name(distribution_title),
            qualifiedName=self._generate_qualified_name(distribution_title),
            longDescription=distribution.description[self._language],
        ).to_json()

        if hasattr(distribution, "identifier"):
            guid = _extract_guid(self._dataset_uri_template, distribution.identifier)
            distribution_term = self._get_persisted_term(guid)

        distribution_term["longDescription"] = distribution.description.get(
            self._language
        )
        distribution_term["seeAlso"] = []

        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.TITLE,
            distribution.title[self._language],
        )

        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.FORMAT,
            _format_value([[item, ""] for item in distribution.formats]),
        )
        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.ACCESS_URL,
            _format_value([[distribution.access_URL, ""]])
            if hasattr(distribution, "access_URL")
            else "",
        )
        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.DOWNLOAD_URL,
            _format_value([[distribution.download_URL, ""]])
            if hasattr(distribution, "download_URL")
            else "",
        )
        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.LICENSE,
            _format_value([[distribution.license, ""]])
            if hasattr(distribution, "license")
            else "",
        )
        self._set_attribute_values(
            distribution_term,
            TermType.DISTRIBUTION,
            Attribute.TEMPORAL_RESOLUTION,
            _format_value([[item] for item in distribution.temporal_resolution])
            if hasattr(distribution, "temporal_resolution")
            else "",
        )

        return distribution_term

    def fetch_glossary(self) -> None:
        """Fetch detailed glossary."""
        self._glossary = self._glossary_client.get_glossary(
            guid=self._glossary_id, detailed=True
        )

    def save_glossary_terms(self) -> None:
        """Save glossary terms.

        Raises:
            InvalidStateError: If there are no terms to save.
        """
        if len(self._tmp_glossary_terms) == 0:
            raise InvalidStateError(
                "No terms to save. Call map_dataset_catalog_to_glossary_terms()."
            )

        dataset_terms = list(
            filter(
                lambda term: self._get_term_type(term) == TermType.DATASET,
                self._tmp_glossary_terms,
            )
        )
        distribution_terms = list(
            filter(
                lambda term: self._get_term_type(term) == TermType.DISTRIBUTION,
                self._tmp_glossary_terms,
            )
        )

        for i in range(len(dataset_terms)):
            original_dataset_guid = dataset_terms[i].get("guid", "")
            if original_dataset_guid.startswith("tmp-"):
                dataset_terms[i].pop("guid")
                dataset_terms[i] = self._glossary_client.upload_term(dataset_terms[i])
            else:
                dataset_terms[i] = self._glossary_client.update_term(dataset_terms[i])

            for j in range(len(distribution_terms)):
                found = False
                for rel in distribution_terms[j].get("seeAlso"):
                    if rel["termGuid"] == original_dataset_guid:
                        found = True
                        rel["termGuid"] = dataset_terms[i].get("guid")

                if found:
                    if distribution_terms[j].get("guid", "").startswith("tmp-"):
                        distribution_terms[j].pop("guid")
                        distribution_terms[j] = self._glossary_client.upload_term(
                            distribution_terms[j]
                        )
                    else:
                        distribution_terms[j] = self._glossary_client.update_term(
                            distribution_terms[j]
                        )

        self.fetch_glossary()

    def map_glossary_terms_to_dataset_catalog(self) -> Catalog:
        """Map glossary terms to dcat dataset catalog RDF resource.

        Returns:
            A catalog RDF resource.

        Raises:
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

        catalog = Catalog()
        catalog.identifier = self._catalog_uri
        catalog.title = {self._language: self._catalog_title}
        catalog.publisher = self._catalog_publisher
        catalog.language = [self._catalog_language]
        catalog.license = ""

        dataset_terms = []
        distribution_terms = []

        # Separate terms based on type
        for term in self.glossary_terms:
            if not self._include_approved_only or (
                self._include_approved_only
                and term.get("status", "").lower() == "approved"
            ):
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

    def map_dataset_catalog_to_glossary_terms(self, catalog: Catalog) -> None:
        """Map dcat dataset catalog RDF resource to glossary terms.

        Args:
            catalog: A dataset catalog RDF resource

        Raises:
            MappingError: A mapping error if the language does not match
            InvalidStateError: If glossary is not fetched before calling this function
        """
        if self._glossary is None:
            raise InvalidStateError(
                "Glossary is undefined. Check if glossary_id is correct and call "
                "fetch_glossary() before calling this function"
            )

        if self._language not in catalog.language:
            raise MappingError("Language in mapper does not match catalog language")

        terms: List = []
        for dataset in catalog.datasets:
            terms = terms + self._map_dataset_to_terms(dataset)

        self._tmp_glossary_terms = terms
