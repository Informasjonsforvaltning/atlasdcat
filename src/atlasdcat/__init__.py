"""atlasdcat package."""
try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from .attribute import Attribute
from .glossaryclient import AtlasGlossaryClient
from .mapper import (
    AtlasDcatMapper,
    FormatError,
    InvalidStateError,
    MappingError,
    TemporalError,
)
from .termtype import TermType
