# SBTi Temperature Alignment tool
This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop 
targets for official validation by the SBTi.

This tool can be used either as a standalone Python package or as an API.

## Structure
The folder structure for this project is as follows:

    .
    ├── .github                 # Github specific files (Github Actions workflows)
    ├── app                     # Flask app files for the API endpoints
    ├── docs                    # Documentation files (Sphinx)
    ├── config                  # Config files for the Docker container
    ├── SBTi                    # The main Python package for the temperature alignment tool
    └── test                    # Automated unit tests for the SBTi package (Nose2 tests)

## Installation
The SBTi package may be installed using PIP. If you'd like to install it locally use the following command:

```bash
pip install -e .
```

## Development
For development purposes, install the SBTi package using the following command:
```bash
pip install -e .[dev]
``` 

### Testing
Each class should be unit tested. The unit tests are written using the Nose2 framework.
The setup.py script should have already installed Nose2, so now you may run the tests as follows:
```bash
nose2 -v
```

## Deployment
The alignment tool can be used either as an standalone Python package or as an API.
The API can be deployed as a Docker container. To do this a Docker file is provided.
To start the docker container locally use the following command:
```bash
docker-compose up -d --build
```
The API should now be available at localhost on port 5000.

### Google Cloud Platform
TODO: document/link to documentation on how to deploy on GCP

### Amazon Web Services
TODO: document/link to documentation on how to deploy on AWS

### Microsoft Azure
TODO: document/link to documentation on how to deploy on Azure