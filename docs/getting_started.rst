********************
Getting Started
********************
The most fundamental part of the project is the Python module. This takes care of all the heavy lifting.
You can install it easily through PIP. There are a couple ways to get started using the module.
The easiest option is to run our getting started notebook on Google Colab. Alternatively you can also run the `getting
started notebooks <https://github.com/OFBDABV/SBTi/tree/master/examples>`_ locally or start from scratch using the API reference.

.. note:: This page only concerns itself with the Python module. The getting started documentation for the REST API can be found on its `dedicated page <https://ofbdabv.github.io/SBTi/rest_api.html>`_. For a distinction between the different parts of the project, have a look at `the homepage <https://ofbdabv.github.io/SBTi/index.html>`_.

Google Colab
-------------
The easiest way to get started is by using the getting started notebook on Google Colab.
It goes through all the steps involved in installing the module and calculating a portfolio score.
There are three notebooks that go through the process, step-by-step:

1. `Analysis <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/1_analysis.ipynb>`_
2. `Getting started <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/2_getting_started.ipynb>`_
3. `Scenarios <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/3_scenarios.ipynb>`_
4. `Portfolio aggregations <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/4_portfolio_aggregations.ipynb>`_
5. `Reporting <https://colab.research.google.com/github/OFBDABV/SBTi/blob/master/examples/5_reporting.ipynb>`_

Jupyter notebooks
-----------------
Alternatively you can also run the getting started notebooks locally. To do so, you first need to setup a new environment.
In the next examples, we'll assume you use Anaconda to manage your environments::

    cd examples
    conda env create -f environment.yml
    activate sbti_getting_started
    jupyter notebook

A tab should now open in your web browser. In case you use virtual env you can install the required packages using the requirements.txt file in the examples directory.
Make sure that your Python version is at least 3.6.

Starting from scratch
---------------------
If you're starting from scratch you can install the latest version of the package directly from Github as follows::

    pip install git+git://github.com/OFBDABV/SBTi

Or you can install the latest stable release from PyPi

    pip install sbti

The `API reference <https://ofbdabv.github.io/SBTi/autoapi/index.html>`_ should provide a clear overview of the module's API and its usage.

.. toctree::
   :maxdepth: 4
