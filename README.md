# Recommendations Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is the Recommendations microservice for the NYU DevOps Fall 2025 eCommerce project.

## Overview

The Recommendations service manages product-to-product relationships to provide intelligent product suggestions to customers. It supports creating, reading, updating, deleting, and listing recommendation relationships between products.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## API Endpoints

### List Recommendations

Retrieve a list of all recommendations, optionally filtered by query parameters.

**Endpoint:** `GET /recommendations`

**Query Parameters:**
- `product_a_id` (integer, optional): Filter by base product ID
- `relationship_type` (string, optional): Filter by relationship type. Valid values:
  - `cross_sell`
  - `up_sell`
  - `accessory`
  - `trending`
- `status` (string, optional): Filter by status. Valid values:
  - `active`
  - `inactive`
  - `draft`
  - `deleted`

**Success Response:**
- **Code:** 200 OK
- **Content:** JSON array of recommendation objects

**Example Requests:**

```bash
# Get all recommendations
curl -X GET "http://localhost:8080/recommendations"

# Filter by product ID
curl -X GET "http://localhost:8080/recommendations?product_a_id=101"

# Filter by relationship type
curl -X GET "http://localhost:8080/recommendations?relationship_type=accessory"

# Filter by status
curl -X GET "http://localhost:8080/recommendations?status=active"

# Multiple filters
curl -X GET "http://localhost:8080/recommendations?product_a_id=101&relationship_type=accessory&status=active"
```

**Example Response:**

```json
[
  {
    "id": 1,
    "base_product_id": 101,
    "recommended_product_id": 202,
    "recommendation_type": "accessory",
    "weighted_score": 8.5,
    "rationale": "Customers who bought this also bought...",
    "status": "active",
    "recommendation_id": 1001,
    "valid_from": "2025-10-13T00:00:00",
    "valid_to": "2025-11-13T00:00:00"
  }
]
```

## Running Tests

To run the test suite:

```bash
make test
```

To run linting:

```bash
make lint
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
