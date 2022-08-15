"""Attribute module for mapping an Atlas Glossery to DCAT rdf."""

from enum import Enum


class Attribute(str, Enum):
    """Attribute enum."""

    ACCESS_RIGHTS = "accessRights"
    ACCESS_URL = "accessURL"
    CONTACT_EMAIL = "contactEmail"
    CONTACT_NAME = "contactName"
    DATASET = "Dataset"
    DISTRIBUTION = "Distribution"
    DOWNLOAD_URL = "downloadURL"
    FORMAT = "format"
    FREQUENCY = "frequency"
    GENERATED = "generated"
    INCLUDE_IN_DCAT = "includeInDCAT"
    KEYWORD = "keyword"
    LICENSE = "license"
    PUBLISHER = "publisher"
    SPATIAL = "spatial"
    SPATIAL_RESOLUTION_IN_METERS = "spatialResolutionInMeters"
    TEMPORAL_START_DATE = "temporalStartDate"
    TEMPORAL_END_DATE = "temporalEndDate"
    TEMPORAL_RESOLUTION = "temporalResolution"
    THEME = "theme"
    TITLE = "title"
