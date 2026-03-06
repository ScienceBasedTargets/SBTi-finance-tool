***********************************
Getting Started Using REST API
***********************************
The REST API wraps this Python package, making it easy to integrate the SBTi temperature alignment tool as a microservice.

For full API documentation, source code, and deployment instructions, see the
`API repository <https://github.com/ScienceBasedTargets/SBTi-finance-tool-api>`_.

Quickstart
====================
Clone the API repository and run with Docker::

    git clone https://github.com/ScienceBasedTargets/SBTi-finance-tool-api.git
    cd SBTi-finance-tool-api
    docker-compose up --build

The API documentation will be available at http://localhost:8000/docs.

Endpoints
====================

- ``GET /health`` -- Health check
- ``GET /v1/data-providers`` -- List configured data providers
- ``POST /v1/temperature/score`` -- Calculate temperature scores
- ``POST /v1/coverage`` -- Calculate portfolio coverage
- ``POST /v1/temperature/whatif`` -- Run what-if scenario analysis
- ``POST /v1/upload/csv`` -- Upload CSV portfolio and score
- ``POST /v1/upload/excel`` -- Upload Excel portfolio and score

.. toctree::
   :maxdepth: 4
