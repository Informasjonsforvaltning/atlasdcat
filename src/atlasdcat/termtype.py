"""Termtype module for mapping an Atlas Glossery to DCAT rdf."""

from enum import Enum


class TermType(Enum):
    """Term type enum."""

    DATASET = 1
    DISTRIBUTION = 2
    UNKNOWN = -1
