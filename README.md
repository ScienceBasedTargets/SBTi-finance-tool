# SBTi Temperature Alignment tool
This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop 
targets for official validation by the SBTi.

This tool can be used either as a standalone Python package, a REST API or as a simple webapp which provides a simple skin on the API.
So, the SBTi toolkit caters for three types of usage:
- Users can integrate the Python package in their codebase 
- The tool can be included as a Microservice (containerised REST API) in any IT infrastructure (in the cloud or on premise)
- As an webapp, exposing the functionality with a simple user interface.

To following diagram provides an overview of the different parts of the toolkit:

    +-------------------------------------------------+
    |   UI     : Simple user interface on top of API  |
    |   Install: via dockerhub              |
    |            docker.io/sbti/ui:latest             |
    |                                                 |
    | +-----------------------------------------+     |
    | | REST API: Dockerized Flask/NGINX        |     |
    | | Source : github.com/OFBDABV/SBTi_api    |     |
    | | Install: via source or dockerhub        |     |
    | |          docker.io/sbti/sbti/api:latest |     |
    | |                                         |     |
    | | +---------------------------------+     |     |
    | | |                                 |     |     |
    | | |Core   : Python Module           |     |     |
    | | |Source : github.com/OFBDABV/SBTi |     |     |
    | | |Install: via source or PyPi      |     |     |
    | | |                                 |     |     |
    | | +---------------------------------+     |     |
    | +-----------------------------------------+     |
    +-------------------------------------------------+

As shown above the API is dependent on the Python Repo, in the same way the UI requires the API backend. These dependencies are scripted in the Docker files

> This repository only contains the Python module. If you'd like to use the REST API, please refer to [this repository](https://github.com/OFBDABV/SBTi_api) or the same repository on [Dockerhub](https://docker.io/sbti/sbti/api:latest).

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
The SBTi package may be installed using PIP. If you'd like to install it locally use the following command. For testing or production please see the deployment section for further instructions

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
