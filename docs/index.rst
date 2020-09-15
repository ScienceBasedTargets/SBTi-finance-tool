SBTi Temperature Alignment tool's documentation
===========================================================
This package helps companies and financial institutions to assess the temperature alignment of current targets,
commitments, and investment and lending portfolios, and to use this information to develop targets for official
validation by the SBTi.

Quickstart
--------------------
To get up-and-running quickly we've got a no-code and a Python option:

* **No-code**: Run the project locally as a `web application using Docker <rest_api.html#locally>`_
* **Python**: Run a Jupyter notebook, without any installation in `Google Colab <getting_started.html#google-colab>`_ or `locally <getting_started.html#jupyter-notebooks>`_.

Project structure
---------------------
This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop
targets for official validation by the SBTi.

This tool can be used either as a standalone Python package, a REST API or as a simple webapp which provides a simple skin on the API.
So, the SBTi toolkit caters for three types of usage:
- Users can integrate the Python package in their codebase
- The tool can be included as a Microservice (containerised REST API) in any IT infrastructure (in the cloud or on premise)
- As an webapp, exposing the functionality with a simple user interface.

To following diagram provides an overview of the different parts of the toolkit::

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
    | | |Source : github.com/OFBDABV/SBTi |     |     |
    | | |Install: via source or PyPi      |     |     |
    | | |                                 |     |     |
    | | +---------------------------------+     |     |
    | +-----------------------------------------+     |
    +-------------------------------------------------+

As shown above the API is dependent on the Python Repo, in the same way the UI requires the API backend. These dependencies are scripted in the Docker files


.. toctree::
   :maxdepth: 4
   :caption: Contents:

   getting_started
   contributing
   rest_api
   1_getting_started