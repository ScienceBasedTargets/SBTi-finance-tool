# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["SBTi", "SBTi.data"]

package_data = {"": ["*"], "SBTi": ["inputs/*"]}

install_requires = [
    "openpyxl>=2.5.0",
    "pandas>=1.0.0",
    "numpy>=1.20.0,<2.0.0",
    "pydantic>=1.0.0,<2.0.0",
    "requests>=2.0.0",
    "six>=1.16.0",
    "xlrd>=2.0.0",
]

setup_kwargs = {
    "name": "sbti-finance-tool",
    "version": "1.2.2",
    "description": "This package helps companies and financial institutions to assess the temperature alignment of current targets, commitments, and investment and lending portfolios, and to use this information to develop targets for official validation by the SBTi.",
    "long_description_content_type": "text/markdown",
    "long_description": "> Visit https://sciencebasedtargets.github.io/SBTi-finance-tool/ for the full documentation\n\n> If you have any additional questions or comments send a mail to: finance@sciencebasedtargets.org\n\n# SBTi Temperature Alignment tool\n\nThis package helps companies and financial institutions to assess the temperature alignment of current\ntargets, commitments, and investment and lending portfolios, and to use this information to develop\ntargets for official validation by the SBTi.\n\nThis tool can be used either as a standalone Python package, a REST API or as a simple webapp which provides a simple skin on the API.\nSo, the SBTi toolkit caters for three types of usage:\n\n- Users can integrate the Python package in their codebase\n- The tool can be included as a Microservice (containerised REST API) in any IT infrastructure (in the cloud or on premise)\n- As an webapp, exposing the functionality with a simple user interface.\n\nTo following diagram provides an overview of the different parts of the toolkit:\n\n    +-------------------------------------------------+\n    |   UI     : Simple user interface on top of API  |\n    |   Install: via dockerhub                        |\n    |            docker.io/sbti/ui:latest             |\n    |                                                 |\n    | +-----------------------------------------+     |\n    | | REST API: Dockerized FastAPI/NGINX      |     |\n    | | Source : github.com/OFBDABV/SBTi_api    |     |\n    | | Install: via source or dockerhub        |     |\n    | |          docker.io/sbti/sbti/api:latest |     |\n    | |                                         |     |\n    | | +---------------------------------+     |     |\n    | | |                                 |     |     |\n    | | |Core   : Python Module           |     |     |\n    | | |Source : github.com/ScienceBasedTargets/     |\n    | | |               SBTi-finance-tool |     |     |\n    | | |Install: via source or PyPi      |     |     |\n    | | |                                 |     |     |\n    | | +---------------------------------+     |     |\n    | +-----------------------------------------+     |\n    +-------------------------------------------------+\n\nAs shown above the API is dependent on the Python Repo, in the same way the UI requires the API backend. These dependencies are scripted in the Docker files.\n\n> This repository only contains the Python module. If you'd like to use the REST API, please refer to [this repository](https://github.com/ScienceBasedTargets/SBTi-finance-tool_api) or the same repository on [Dockerhub](https://docker.io/sbti/sbti/api:latest).\n\n## Structure\n\nThe folder structure for this project is as follows:\n\n    .\n    ├── .github                 # Github specific files (Github Actions workflows)\n    ├── app                     # FastAPI app files for the API endpoints\n    ├── docs                    # Documentation files (Sphinx)\n    ├── config                  # Config files for the Docker container\n    ├── SBTi                    # The main Python package for the temperature alignment tool\n    └── test                    # Automated unit tests for the SBTi package (Nose2 tests)\n\n## Installation\n\nThe SBTi package may be installed using PIP. If you'd like to install it locally use the following command. For testing or production please see the deployment section for further instructions\n\n```bash\npip install -e .\n```\n\nFor installing the latest stable release in PyPi run:\n\n```bash\npip install sbti\n```\n\n## Development\n\nTo set up the local dev environment with all dependencies, [install poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) and run\n\n```bash\npoetry install\n```\n\nThis will create a virtual environment inside the project folder under `.venv`.\n\n### Testing\n\nEach class should be unit tested. The unit tests are written using the Nose2 framework.\nThe setup.py script should have already installed Nose2, so now you may run the tests as follows:\n\n```bash\nnose2 -v\n```\n\n### Publish to PyPi\n\nThe package should be published to PyPi when any changes to main are merged.\n\nUpdate package\n\n1. bump version in `pyproject.toml` based on semantic versioning principles\n2. run `poetry build`\n3. run `poetry publish`\n4. check whether package has been successfully uploaded\n\n**Initial Setup**\n\n- Create account on [PyPi](https://pypi.org/)\n",
    "author": "sbti",
    "author_email": "financialinstitutions@sciencebasedtargets.org",
    "maintainer": None,
    "maintainer_email": None,
    "url": None,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.7.1",
}


setup(**setup_kwargs)
