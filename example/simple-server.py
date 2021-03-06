#!/usr/bin/env python3
"""Very simple HTTP server in python for demo purposes.

Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
from typing import Any

from dotenv import load_dotenv
from pyapacheatlas.auth import BasicAuthentication, ServicePrincipalAuthentication
from pyapacheatlas.core.glossary import GlossaryClient

from atlasdcat import AtlasDcatMapper, Attribute

load_dotenv()


class Handler(BaseHTTPRequestHandler):
    """Handle requests."""

    def _set_ok_response(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/turtle")
        self.end_headers()

    def _set_error_response(self) -> None:
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        logging.info(
            "GET request, Path: %s Headers:%s", str(self.path), str(self.headers)
        )

        auth = BasicAuthentication(
            username=os.getenv("BASIC_AUTH_USERNAME", ""),
            password=os.getenv("BASIC_AUTH_PASSWORD", ""),
        )

        if os.getenv("SERVICE_PRINCIPLE_TENANT_ID") != "":
            auth = ServicePrincipalAuthentication(
                tenant_id=os.getenv("SERVICE_PRINCIPLE_TENANT_ID", ""),
                client_id=os.getenv("SERVICE_PRINCIPLE_CLIENT_ID", ""),
                client_secret=os.getenv("SERVICE_PRINCIPLE_CLIENT_SECRET", ""),
            )

        atlas_client = GlossaryClient(
            endpoint_url=os.getenv("ATLAS_ENDPOINT_URL", ""), authentication=auth
        )

        mapper = AtlasDcatMapper(
            glossary_client=atlas_client,
            glossary_id="ef38fdb9-bbd5-4c5e-92fd-30bebc07a3f1",
            catalog_uri="https://domain/catalog",
            catalog_title="Catalog",
            catalog_publisher="https://domain/publisher",
            dataset_uri_template="http://domain/datasets/{guid}",
            distribution_uri_template="http://domain/distributions/{guid}",
            language="nb",
            attr_mapping={
                Attribute.ACCESS_RIGHTS: "Tilgangsniv??",
                Attribute.ACCESS_URL: "TilgangsUrl",
                Attribute.CONTACT_EMAIL: "DataeierEpost",
                Attribute.CONTACT_NAME: "Dataeier",
                Attribute.DATASET: "Datasett",
                Attribute.DISTRIBUTION: "Distribusjon",
                Attribute.DOWNLOAD_URL: "Nedlastningslenke",
                Attribute.FORMAT: "Format",
                Attribute.FREQUENCY: "Oppdateringsfrekvens",
                Attribute.INCLUDE_IN_DCAT: "PubliseresP??FellesDatakatalog",
                Attribute.KEYWORD: "Emneord",
                Attribute.LICENSE: "Lisens",
                Attribute.PUBLISHER: "Utgiver",
                Attribute.SPATIAL: "GeografiskAvgrensning",
                Attribute.SPATIAL_RESOLUTION_IN_METERS: "GeografiskOppl??sning",
                Attribute.THEME: "Tema",
                Attribute.TITLE: "Tittel",
                Attribute.TEMPORAL_START_DATE: "StartP??Perioden",
                Attribute.TEMPORAL_END_DATE: "SluttP??Perioden",
                Attribute.TEMPORAL_RESOLUTION: "PeriodeOppl??sning",
            },
        )

        try:
            catalog = mapper.map_glossary_to_dcat_dataset_catalog()
            print(catalog)

            self._set_ok_response()
            self.wfile.write(catalog.to_rdf())
        except Exception as e:
            self._set_error_response()
            self.wfile.write(f"An error occurred: {e}".encode("utf-8"))


def run(
    server_class: Any = HTTPServer, handler_class: Any = Handler, port: int = 8081
) -> None:
    """Set up and start simple server."""
    logging.basicConfig(level=logging.INFO)
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    logging.info(f"Starting httpd at port {port}...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
