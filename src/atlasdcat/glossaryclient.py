"""AtlasClient module for mapping an Atlas Glossery to DCAT rdf."""
from typing import Dict, Union

from pyapacheatlas.auth import ServicePrincipalAuthentication
from pyapacheatlas.core.glossary import _CrossPlatformTerm, GlossaryClient
import requests


class AtlasGlossaryClient(GlossaryClient):
    """Class for Atlas Glossary REST Client."""

    def __init__(
        self,
        endpoint_url: str,
        authentication: ServicePrincipalAuthentication,
        **kwargs: Dict,
    ) -> None:
        """Initializes an AtlasGlossaryClient."""
        super().__init__(endpoint_url, authentication, **kwargs)

    def update_term(
        self, term: Union[Dict, _CrossPlatformTerm], **kwargs: Dict
    ) -> Dict:
        """Update a single term to Apache Atlas.

        Provide an AtlasGlossaryTerm or dictionary.

        Args:
            term: The term to be updated.
            kwargs: The parameters to pass into the url.

        Returns:
            The updated term's current state.

        Raises:
            TypeError: A type error
        """
        if isinstance(term, dict):
            payload = term
        elif isinstance(term, _CrossPlatformTerm):
            payload = term.to_json()
        else:
            raise TypeError(
                f"The type {type(term)} is not supported. Please use a dict, "
                f"AtlasGlossaryTerm, or PurviewGlossaryTerm"
            )

        atlas_endpoint = "{endpoint}/glossary/term/{guid}".format(
            endpoint=self.endpoint_url, guid=payload.get("guid")
        )

        put_resp = requests.put(
            atlas_endpoint,
            json=payload,
            params=kwargs.get("parameters", {}),
            headers=self.authentication.get_authentication_headers(),
            **self._requests_args,
        )

        results = self._handle_response(put_resp)

        return results
