> Visit https://sciencebasedtargets.github.io/SBTi-finance-tool/ for the full documentation

> If you have any additional questions or comments send a mail to: financialinstitutions@sciencebasedtargets.org

# SBTi Temperature Alignment tool

> **Note:** This tool implements [**Version 1.0**](https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf) of the CDP/WWF Temperature Rating Methodology, for setting and reporting on SBTi Financial Institutions Near-Term Targets. For Version 1.5 of the methodology, please refer to the [CDP-WWF Temperature Scoring Methodology](https://www.cdp.net/en/data-licenses/net-zero-alignment-dataset/the-cdp-wwf-temperature-scoring-methodology).

This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop
targets for official validation by the SBTi.

This tool can be used as a standalone Python package or as a containerised REST API.

- **Python package**: Integrate directly into your codebase or run via Jupyter notebooks
- **REST API**: Deploy as a microservice using the [SBTi Finance Tool API](https://github.com/ScienceBasedTargets/SBTi-finance-tool-api)

> This repository contains the Python package. For the REST API, see the [API repository](https://github.com/ScienceBasedTargets/SBTi-finance-tool-api).

## Structure

The folder structure for this project is as follows:

    .
    ├── .github                 # Github specific files (Github Actions workflows)
    ├── docs                    # Documentation files (Sphinx)
    ├── examples                # Jupyter notebook examples
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
