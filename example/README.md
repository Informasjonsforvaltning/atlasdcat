# example

Very simple server exposing an API with the DCAT-representation.

NOT suited for production use

## Requirements

.env in a basic auth scenario:

```Shell
BASIC_AUTH_USERNAME=dummy
BASIC_AUTH_ATLAS_PASSWORD=dummy
ATLAS_ENDPOINT_URL=http://your.atlas.host.com/api/atlas/v2
```

If you run against openID connect (e.g. in Azure Purview scenario), this is what you need to put in your .env:

```Shell
SERVICE_PRINCIPLE_TENANT_ID=
SERVICE_PRINCIPLE_CLIENT_ID=
SERVICE_PRINCIPLE_CLIENT_SECRET=very_secret_secret
ATLAS_ENDPOINT_URL=http://your.purview.host.com/catalog/api/atlas/v2
```

## Setup local Apache Atlas server

```Shell
cd atlas
docker-compose up
```

After building the atlas docker image, docker-compose will start the following
services: atlas-server, kafka and zookeeper. Starting the Apache Atlas server
can take up to 10 minutes. Be patient.

Wait for the following message:

```Shell
atlas-server_1 | Apache Atlas Server started!!!
atlas-server_1 | 
atlas-server_1 | waiting for atlas to be ready
atlas-server_1 | .....
atlas-server_1 | Server: Apache Atlas
...
atlas-server_1 | glossary created
atlas-server_1 | Done setting up Atlas
```

Configuration (.env file)

```Shell
GLOSSARY_ID=xxxx
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_ATLAS_PASSWORD=admin
ATLAS_ENDPOINT_URL=http://localhost:21000/api/atlas/v2
```

Run following command to get the glossary ID

```Shell
curl -u admin:admin  http://localhost:21000/api/atlas/v2/glossary
```

This will output something like this. Look for the value for "guid".

```Shell
[{"guid":"2c453c5e-6d47-4fcc-ae17-d1753ab72abb","qualifiedName":"myglossary",
"name":"myglossary", "terms":[{"termGuid":"0181bc5d-58aa-4194-8c5e-c8267a305ead",
"relationGuid":"1d94e821-bf9e-4d12-b145-35b66d5be2ee","displayText":"dataset"}]}]
```

## Usage

```Shell
% poetry run python simple-server.py
```

In another shell:

Fetch data catalog as RDF
```Shell
% curl http://localhost:8081/catalog
```

Save data catalog as Glossary Terms to Apache Atlas. 

The dataset identifier should be omitted when a dataset does not exist in Atlas. The mapper will generate an identifier.
```Shell
% curl -X POST -H "Content-Type: application/json" \
    -d '{ 
        "_type": "Catalog",
        "access_rights_comments": [],
        "catalogrecords": [
            {
                "_type": "CatalogRecord",
                "conforms_to": [],
                "identifier": "http://example.com/catalog-record/1"
            }
        ],
        "conforms_to": [],
        "datasets": [
            {
                "_type": "Dataset",
                "access_rights_comments": [],
                "conforms_to": [],
                "distributions": [],
                "frequency": "http://WEEKLY",
                "is_referenced_by": [],
                "landing_page": [],
                "language": [],
                "qualified_attributions": [],
                "qualified_relation": [],
                "resource_relation": [],
                "theme": [],
                "title": {"en": "Dataset 1", "nb": "Datasett 1"},
                "description": {"en": "Dataset 1 description", "nb": "Datasett 1 beskrivelse"}
            },
            {
                "_type": "Dataset",
                "access_rights_comments": [],
                "conforms_to": [],
                "distributions": [],
                "is_referenced_by": [],
                "landing_page": [],
                "language": [],
                "qualified_attributions": [],
                "qualified_relation": [],
                "resource_relation": [],
                "theme": [],
                "title": {"en": "Dataset 2", "nb": "Datasett 2"},
                "description": {"en": "Dataset 2 description", "nb": "Datasett 2 beskrivelse"}
            }
        ],
        "description": {"en": "Description", "nb": "Beskrivelse"},
        "identifier": "http://example.com/catalogs/1",
        "is_referenced_by": [],
        "landing_page": [],
        "language": ["en", "nb"],
        "qualified_attributions": [],
        "qualified_relation": [],
        "resource_relation": [],
        "themes": [],
        "title": {"en": "This catalog", "nb": "Denne katalogen"}
    }' \
    http://localhost:8081/catalog
```