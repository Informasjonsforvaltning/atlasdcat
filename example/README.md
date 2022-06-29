# example

Very simple server exposing an API with the DCAT-represenation.

NOT suited for production use

## Requirements

.env in a basic auth scenario:

```Shell
BASIC_AUTH_USERNAME=dummy
BASIC_AUTH_ATLAS_PASSWORD=dummy
ATLAS_ENDPOINT_URL=http://your.atlas.host.com/
```

If you run against openID connect (e.g. in Azure Purview scenario), this is what you need to put in your .env:

```Shell
SERVICE_PRINCIPLE_TENANT_ID=
SERVICE_PRINCIPLE_CLIENT_ID=
SERVICE_PRINCIPLE_CLIENT_SECRET=very_secret_secret
ATLAS_ENDPOINT_URL=http://your.purview.host.com/catalog
```

## Usage

```Shell
% poetry run python simple-server.py
```

In another shell:

```Shell
% curl http://localhost:8081/catalog
```
