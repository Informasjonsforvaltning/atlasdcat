"""Test cases for the mapper module."""
import json
from typing import Any

from pyapacheatlas.auth import BasicAuthentication
from pyapacheatlas.core.glossary import AtlasGlossaryTerm
import pytest

from atlasdcat import (
    AtlasGlossaryClient,
)


def test_update_term_with_dict(
    responses: Any,
) -> None:
    """Test update term with dict."""
    with open(
        "tests/files/mock_glossary_term_dataset1_changed_response.json", "r"
    ) as f1:
        dataset1_json_response = json.loads(f1.read())

    responses.add(
        method=responses.PUT,
        url="http://atlas/glossary/term/24656c6d-0479-43b3-9bda-c1c93ab09010",
        json=dataset1_json_response,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    response = atlas_client.update_term(dataset1_json_response)
    assert response == dataset1_json_response


def test_update_term_with_object(
    responses: Any,
) -> None:
    """Test update term with AtlasGlossaryTerm object."""
    with open("tests/files/mock_atlas_glossary_term_dataset_response.json", "r") as f1:
        dataset_json_response = json.loads(f1.read())

    term = AtlasGlossaryTerm(
        guid="24656c6d-0479-43b3-9bda-c1c93ab09010",
        qualifiedName="atlasdataset@myglossary",
        name="atlasdataset",
        longDescription="Atlas dataset description",
        anchor={
            "glossaryGuid": "myglossary",
            "relationGuid": "4f98e85a-73f8-4548-80fe-30799888a0e6",
        },
        additionalAttributes={
            "Datasett": {
                "Dataeier": "",
                "DataeierEpost": "",
                "Emneord": "",
                "GeografiskAvgrensning": "",
                "Lisens": "",
                "Oppdateringsfrekvens": "",
                "Tema": "",
                "Tilgangsnivå": "",
                "Tittel": "Atlas dataset",
                "Utgiver": "",
                "spatialResolutionInMeters": "",
                "temporalEndDate": "",
                "temporalStartDate": "",
            }
        },
    )

    responses.add(
        method=responses.PUT,
        url="http://atlas/glossary/term/24656c6d-0479-43b3-9bda-c1c93ab09010",
        json=dataset_json_response,
    )

    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    response = atlas_client.update_term(term)
    assert response == term.to_json()


def test_update_term_with_invalid_type(
    responses: Any,
) -> None:
    """Test update with invalid type."""
    atlas_auth = BasicAuthentication(username="", password="")  # noqa: S106
    atlas_client = AtlasGlossaryClient(
        endpoint_url="http://atlas", authentication=atlas_auth
    )

    with pytest.raises(TypeError):
        atlas_client.update_term([])
