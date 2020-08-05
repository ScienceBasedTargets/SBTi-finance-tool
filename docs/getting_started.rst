********************
Getting Started
********************
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


Python module
====================
The most fundamental part of the project is the Python module. This takes care of all the heavy lifting.
You can install it easily through PIP. There are a couple ways to get started using the module.
The easiest option is to run our getting started notebook on Google Colab. Alternatively you can also run the `getting
started notebooks <https://github.com/OFBDABV/SBTi/tree/master/examples>`_ locally or start from scratch using the API reference.

Google Colab
-------------
The easiest way to get started is by using the getting started notebook on Google Colab.
It goes through all the steps involved in installing the module and calculating a portfolio score.
The example notebook can be found `here <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/1_getting_started-colab.ipynb>`_.

Jupyter notebooks
-----------------
Alternatively you can also run the getting started notebooks locally. To do so, you first need to setup a new environment.
In the next examples, we'll assume you use Anaconda to manage your environments::

    cd examples
    conda env create -f environment.yml
    jupyter notebook

A tab should now open in your web browser. In case you use virtual env you can install the required packages using the requirements.txt file in the examples directory.

Installation
====================
TODO: Installation instructions

Examples
====================
TODO: Write some examples

.. toctree::
   :maxdepth: 4
