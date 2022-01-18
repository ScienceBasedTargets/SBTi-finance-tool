****************************
Getting Started Using Python
****************************
The most fundamental part of the project is the Python module, which takes care of all the heavy lifting. 
You can install it easily through PIP. There are a couple ways to get started using the module. 
The easiest option is to run our getting started notebook on `Google Colab <https://colab.research.google.com/>`__.
Alternatively, you can also run the `notebooks <https://github.com/ScienceBasedTargets/SBTi-finance-tool/tree/master/examples>`__ locally or start from scratch using the API reference.

.. note:: This page focuses on the Python module. The getting started documentation for the REST API can be found on its `dedicated page <https://ofbdabv.github.io/SBTi/rest_api.html>`__. For a distinction between the different parts of the project, have a look at `the homepage <https://ofbdabv.github.io/SBTi/index.html>`__.

Google Colab
-------------
The easiest way to get started is by using the getting started notebook on Google Colab. 
It guides you through all the steps involved in installing the module and consequently running it, i.e. calculating a temperature scores and analyzing portfolios. 
There are five notebooks that go through the process step-by-step:

We recommend that you start with notebook 1 analysis example, especially
if you are new to Python and/or the `temperature scoring
methodology <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__.

1. `Analysis example (with abbreviated methodology) <https://colab.research.google.com/github/ScienceBasedTargets/SBTi-finance-tool/blob/main/examples/1_analysis_example.ipynb>`__
2. `Quick temperature calculation <https://colab.research.google.com/github/ScienceBasedTargets/SBTi-finance-tool/blob/main/examples/2_quick_temp_score_calculation.ipynb>`__
3. `What-if analysis <https://colab.research.google.com/github/ScienceBasedTargets/SBTi-finance-tool/blob/main/examples/3_what-if-analysis.ipynb>`__
4. `Portfolio aggregation <https://colab.research.google.com/github/ScienceBasedTargets/SBTi-finance-tool/blob/main/examples/4_portfolio_aggregations.ipynb>`__
5. `Reporting <https://colab.research.google.com/github/ScienceBasedTargets/SBTi-finance-tool/blob/main/examples/5_reporting.ipynb>`__

Jupyter Notebooks
-----------------
Alternatively, you can also run the notebooks locally. To do so, you first need to set-up a new environment.
In this example, we assume you use `Anaconda <https://www.anaconda.com/>`__ to manage your environments. 
To do this, run the following command::

    cd examples conda env create -f environment.yml activate sbti_getting_started jupyter notebook

A tab should now open in your web browser. If you are using a virtual environment, you can install the required packages using the requirements.txt file in the examples directory. 
Make sure that your Python version is at least 3.7.

Python code
---------------------
If you are starting from scratch, you can install the latest version of the package directly from Github as follows::

    pip install git+git://github.com/ScienceBasedTargets/SBTi-finance-tool

Or you can install the latest stable release from PyPi

    pip install sbti

The `API reference <https://ofbdabv.github.io/SBTi/autoapi/index.html>`_ should provide a clear overview of the module's API and its usage.

.. toctree::
   :maxdepth: 4
