********************
Contributing
********************
Any contribution is highly appreciated. The most common way to get
contribute to the project is through coding, however contributions to
the documentation are also very welcome.

Submitting a bug report or a feature request
==============================================
To keep track of open issues and feature requests, we use `Github's issue tracker <https://github.com/OFBDABV/SBTi/issues/>`_.

If you encounter any bugs or missing features, please don't hesitate to open a ticket. However, before submitting a new issue, please check that there isn't already another issue or pull request that addresses your issue.

To make sure that others know exactly what the problem is, the ticket should have the following characteristics:

* Reproducible: It should be possible for other to reproduce the issue, ideally through a small code snippet in the description of the issue
* Labelled: Add a label that describes the contents of the ticket, e.g. "bug", "feature request" or "documentation"

Contributing code
====================
The preferred way for contributing code is to fork the repository, make changes on your personal fork and then create a pull request to merge your changes back into the main repository.
Before a pull request can be approved it needs to be reviewed by two core contributors and the automated checks need to be passed (more on these checks can be found in the "Coding guidelines" section below).

.. note:: When you're starting work on an issue, assign yourself to it, this way we avoid duplicate work.

Getting started
-----------------
The easiest way to work on the Python module is by installing it in development mode. This can be done using the following command::

    pip install -e .[dev]

This will install the module as a reference to your current directory.
The Jupyter notebooks in the "examples" directory have been setup to use auto-reload. Thus, if you now make any changes to your local code, they will be automatically reflected in the notebook.

Coding guidelines
-------------------
In general the code follows three principals, `OOP <https://en.wikipedia.org/wiki/Object-oriented_programming>`_, `PEP8 (code style) <https://www.python.org/dev/peps/pep-0008/>`_ and `PEP 484 (type hinting) <https://www.python.org/dev/peps/pep-0484/>`_.
In addition, we use Flake8 to lint the code, MyPy to check the type hints and Nose2 to do unit testing. These checks are done automatically when attempting to merge a pull request into master.

Code of conduct
===============
Everyone is here with the same goal, helping portfolio holders decrease their impact on climate change.
The only way this goal can be achieved is in an inclusive and welcoming environment. Therefore this project is governed by a `code of conduct <https://github.com/OFBDABV/SBTi/blob/master/CODE_OF_CONDUCT.md>`_. By participating, you are expected to uphold this code. If you encounter any violations, please report them to the SBTi: finance@sciencebasedtargets.org .

.. toctree::
   :maxdepth: 4
