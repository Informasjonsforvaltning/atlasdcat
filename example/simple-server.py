#!/usr/bin/env python3
"""Very simple HTTP server in python for demo purposes.

Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
from typing import Any

from datacatalogtordf import Catalog, Dataset
from dotenv import load_dotenv
from pyapacheatlas.auth import BasicAuthentication, ServicePrincipalAuthentication

from atlasdcat import AtlasDcatMapper, AtlasGlossaryClient, Attribute

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

    def _create_mapper(self):
        auth = BasicAuthentication(
            username=os.getenv("BASIC_AUTH_USERNAME", ""),
            password=os.getenv("BASIC_AUTH_PASSWORD", ""),
        )

        if os.getenv("SERVICE_PRINCIPLE_TENANT_ID", "") != "":
            auth = ServicePrincipalAuthentication(
                tenant_id=os.getenv("SERVICE_PRINCIPLE_TENANT_ID", ""),
                client_id=os.getenv("SERVICE_PRINCIPLE_CLIENT_ID", ""),
                client_secret=os.getenv("SERVICE_PRINCIPLE_CLIENT_SECRET", ""),
            )

        atlas_client = AtlasGlossaryClient(
            endpoint_url=os.getenv("ATLAS_ENDPOINT_URL", ""), authentication=auth
        )

        mapper = AtlasDcatMapper(
            glossary_client=atlas_client,
            glossary_id=os.getenv("GLOSSARY_ID", ""),
            catalog_uri="https://domain/catalog",
            catalog_language="http://publications.europa.eu/resource/authority/language/NOB",
            catalog_title="Catalog",
            catalog_publisher="https://domain/publisher",
            dataset_uri_template="http://domain/datasets/{guid}",
            distribution_uri_template="http://domain/distributions/{guid}",
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

        return mapper

    def do_GET(self) -> None:
        """Handle GET requests."""
        logging.info(
            "GET request, Path: %s Headers:%s", str(self.path), str(self.headers)
        )

        mapper = self._create_mapper()
        try:
            mapper.fetch_glossary()
            catalog = mapper.map_glossary_terms_to_dataset_catalog()
            print(catalog)

            self._set_ok_response()
            self.wfile.write(catalog.to_rdf())
        except Exception as e:
            self._set_error_response()
            self.wfile.write(f"An error occurred: {e}".encode("utf-8"))

    def do_POST(self) -> None:
        """Handle GET requests."""
        logging.info(
            "GET request, Path: %s Headers:%s", str(self.path), str(self.headers)
        )

        mapper = self._create_mapper()

        catalog = Catalog()
        catalog.identifier = "http://catalog-uri"
        catalog.title = {"nb": "mytitle"}
        catalog.publisher = "http://publisher"
        catalog.language = ["nb"]
        catalog.license = ""

        dataset = Dataset()
        dataset.title = {"nb": "Dataset"}
        dataset.description = {"nb": "Dataset description"}
        catalog.datasets = [dataset]

        try:
            mapper.fetch_glossary()
            mapper.map_dataset_catalog_to_glossary_terms(catalog)
            mapper.save_glossary_terms()
        except Exception as e:
            print(f"An exception occurred: {e}")


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
