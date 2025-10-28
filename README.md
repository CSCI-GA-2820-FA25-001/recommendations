# NYU DevOps Project Recommendations Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-FA25-001/recommendations/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-001/recommendations/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-001/recommendations/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-FA25-001/recommendations)

This is the Recommendations microservice for the NYU DevOps Fall 2025 eCommerce project.

[![Build Status](https://github.com/CSCI-GA-2820-FA25-001/recommendations/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-001/recommendations/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-001/recommendations/graph/badge.svg?token=Z8BYACFCO2)](https://codecov.io/gh/CSCI-GA-2820-FA25-001/recommendations)

## Overview

The Recommendations service manages product-to-product relationships to provide intelligent product suggestions to customers. It implements a REST API that supports __creating__, __reading__, __updating__, __deleting__, and __listing__ recommendation relationships between products.

The `/service` folder contains files for the database model and the service. The `/test` file separately contains files for testing the model and the service.

All API endpoints in this service return __JOSN__-formatted responses, including those error messages.

## Setup

Clone the repository and open it in VSCode:
```bash
    git clone git@github.com:CSCI-GA-2820-FA25-001/recommendations.git
    cd recommendations
    code .
```
If using the VSCode Remote Container, please click the automated poped-up instruction "Reopen in Container".

## Run the Service
```bash
flask run
```
Once running, open the browser and visit the corresponding localhost.

## Test the Codes
All tests are located in the /tests folder:
* test_models.py - tests the data model
* test_routes.py - tests the REST API routes
* factories.py - creates fake data for testing

__Run all tests__:
```bash
flask db-create
make test
```

__Run linter for PEP8 style__
```bash
make lint
```

This project follows Test-Driven Development(TDD) pratices and includes complete model and route tets with at lease 95% code coverage.

## API Endpoints

__Recommendations__

Method | Endpoint | Description | Response
--- | --- | --- | ---
GET | /recommendations | List all recommendations | 200_OK
POST | /recommendations | Create a new recommendation | 201_CREATED
GET | /recommendations/id | Read a specific recommendation | 200_OK
PUT | /rexommendations/id | Update an existing recommendation | 200_OK
DELETE | /recommendations/id | Delete a recommendation | 204_NO_CONTENT

## Recommendation Examples
```json
{
    "id": 1,
    "name": "Alpha",
    "base_product_id": 100,
    "recommended_product_id": 201,
    "recommendation_type": "trending",
    "status": "draft",
    "created_at": "2025-10-12",
    "updated_at": "2025-10-14"
}
{
    "id": 98,
    "name": "Beta",
    "base_product_id": 177,
    "recommended_product_id": 245,
    "recommendation_type": "cross_sell",
    "status": "active",
    "created_at": "2023-06-29",
    "updated_at": "2025-08-06"
}
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
