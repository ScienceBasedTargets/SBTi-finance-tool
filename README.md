> Visit https://sciencebasedtargets.github.io/SBTi-finance-tool/ for the full documentation

> If you have any additional questions or comments send a mail to: financialinstitutions@sciencebasedtargets.org

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
    |   Install: via dockerhub                        |
    |            docker.io/sbti/ui:latest             |
    |                                                 |
    | +-----------------------------------------+     |
    | | REST API: Dockerized FastAPI/NGINX      |     |
    | | Source : github.com/OFBDABV/SBTi_api    |     |
    | | Install: via source or dockerhub        |     |
    | |          docker.io/sbti/sbti/api:latest |     |
    | |                                         |     |
    | | +---------------------------------+     |     |
    | | |                                 |     |     |
    | | |Core   : Python Module           |     |     |
    | | |Source : github.com/ScienceBasedTargets/     |
    | | |               SBTi-finance-tool |     |     |
    | | |Install: via source or PyPi      |     |     |
    | | |                                 |     |     |
    | | +---------------------------------+     |     |
    | +-----------------------------------------+     |
    +-------------------------------------------------+

As shown above the API is dependent on the Python Repo, in the same way the UI requires the API backend. These dependencies are scripted in the Docker files.

> This repository only contains the Python module. If you'd like to use the REST API, please refer to [this repository](https://github.com/ScienceBasedTargets/SBTi-finance-tool-api) or the same repository on [Dockerhub](https://docker.io/sbti/sbti/api:latest).

## Structure

The folder structure for this project is as follows:

    .
    ├── .github                 # Github specific files (Github Actions workflows)
    ├── app                     # FastAPI app files for the API endpoints
    ├── docs                    # Documentation files (Sphinx)
    ├── config                  # Config files for the Docker container
    ├── SBTi                    # The main Python package for the temperature alignment tool
    └── test                    # Automated unit tests for the SBTi package (Nose2 tests)

## Installation

The SBTi package may be installed using PIP. If you'd like to install it locally use the following command. For testing or production please see the deployment section for further instructions

```bash
pip install -e .
```

For installing the latest stable release in PyPi run:

```bash
pip install sbti-finance-tool
```

## Development

To set up the local dev environment with all dependencies, [install poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) and run

```bash
poetry install
```

This will create a virtual environment inside the project folder under `.venv`.

### SBTi Companies Taking Action (CTA) Data

The tool supports multiple formats of the SBTi CTA file:
- **Per-company format** (default, recommended): One row per company with aggregated target status
- **Per-target format**: Multiple rows per company with detailed target information
- **Legacy format**: Original Title Case column format

The tool automatically detects and handles all formats, defaulting to the per-company format for consistency.

### Testing

Each class should be unit tested. The unit tests are written using the Nose2 framework.
The setup.py script should have already installed Nose2, so now you may run the tests as follows:

```bash
nose2 -v
```

### Publish to PyPi

The package should be published to PyPi when any changes to main are merged.

Update package

1. bump version in `pyproject.toml` based on semantic versioning principles
2. run `poetry build`
3. run `poetry publish`
4. check whether package has been successfully uploaded

**Initial Setup**

- Create account on [PyPi](https://pypi.org/)
