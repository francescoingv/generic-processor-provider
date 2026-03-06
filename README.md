
# Generic processor provider for pygeoapi plugins

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18892842.svg)](https://doi.org/10.5281/zenodo.18892842)

This repository contains a **Flask web application** that implements a
generic execution service used as an **external processing service**
for the plugins defined in the project:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins

The service receives execution requests through HTTP APIs, invokes
an application code through the command line, and returns the
execution status and results.

The project is designed as a backend component for executing remote
processing tasks and uses an external system (PostgreSQL) to record
execution information.

------------------------------------------------------------------------

## Overview

The service is designed to be used together with the **INGV pygeoapi
process plugins**, which implement processes compatible with the
**OGC API - Processes** standard.

In this architecture:

- **pygeoapi** exposes processes through standard APIs
- **pygeoapi plugins** manage execution requests
- this service executes the requested application code

The execution of the codes takes place in a separate service,
allowing:

- isolation of execution environments
- independent management of dependencies
- greater flexibility in deployment

------------------------------------------------------------------------

## Execution workflow

The service exposes HTTP endpoints used by pygeoapi plugins.

Simplified workflow:

1. the pygeoapi plugin receives an execution request
2. the plugin sends an HTTP request to this service
3. the service invokes the configured application code on the local machine
4. the code is executed and the service collects the execution result
5. the service returns the result to the plugin
6. the results can be retrieved through the APIs exposed by pygeoapi

------------------------------------------------------------------------

## Configuration

The service configuration is defined through two main files.

### `application.ini`

Defines application parameters and the command used to execute the code.

Main parameters:

- `max_allowed_parameter_len`  
  maximum length of a parameter name

- `max_allowed_request_body_size`  
  maximum size of the HTTP request body

- `id_service`  
  identifier of the service

- `command_line`  
  command used to execute the application code

- `suppress_stdout`  
  indicates whether the standard output of the process must be suppressed

- `file_root_directory`  
  directory used for input and output files

### `database.ini`

Defines the connection parameters to the PostgreSQL database used
to manage requests and job status.

Example:

```ini
[postgresql]
host=127.0.0.1
port=5433
database=ogc_api
user=ogc_api_user
password=user
```

### Database schema

The service requires a PostgreSQL schema for storing execution
requests and job status.

The schema is provided in the file:

```text
postgresql_schema.backup.sql
```

Before starting the service, the database must be created and the
schema imported. For example:

```bash
psql -U ogc_api_user -d ogc_api -f postgresql_schema.backup.sql
```

The schema creates the main tables used by the service:

- `request`
- `request_parameter`

The `request` table stores information about received jobs and their
execution status.

The `request_parameter` table stores parameters associated with each
request.

The user configured in `database.ini` must have access permissions
to the tables and sequences defined in the schema.

### Configuration files

The main configuration files of the service are:

- `va_simple_provider/application.ini`
- `va_simple_provider/database.ini`
- `va_simple_provider/logging.cfg`

Before starting the service, verify in particular the database
connection parameters defined in `database.ini`.

## Processing codes

The execution service is designed to run external scientific
processing codes configured through the `command_line` parameter
in the `application.ini` configuration file.

Current deployments of the platform execute the following codes:

- **solwcad**
- **conduit**
- **pybox**

The execution service invokes these codes through command-line
execution and returns the results to the pygeoapi plugins.

These processing codes are not part of this repository and must
be installed separately depending on the deployment environment.

------------------------------------------------------------------------

## Service API

### Execute a job

```text
POST /execute
```

The request body must contain a JSON object with the execution
parameters.

### Job information

```text
GET /job_info/<job_id>
```

Returns the execution status and job information.

------------------------------------------------------------------------

## Project structure

```text
generic-processor-provider/
├── requirements.txt
├── postgresql_schema.backup.sql
├── va_simple_provider/
│   ├── __init__.py
│   ├── application.ini
│   ├── database.ini
│   ├── logging.cfg
│   ├── views.py
│   ├── db_utils.py
│   ├── custom_exceptions.py
│   └── controllers/
│       └── code_handler.py
└── README.md
```

---

## Docker deployment

The repository is designed to be deployed using Docker containers.

The included `Dockerfile`:

- installs the Flask application
- configures the application parameters
- installs Python dependencies
- starts the HTTP service

The service is exposed on port:

```text
5000
```

------------------------------------------------------------------------

## Requirements

Main dependencies:

- Python ≥ 3.12
- Flask
- PostgreSQL
- psycopg2
- virtualenv / venv-run

Python dependencies are defined in the `requirements.txt` file.

------------------------------------------------------------------------

## Relation with other projects

This project implements the **external processing service**
used by the plugins defined in the repository:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins

pygeoapi plugins send HTTP requests to this service to execute
application codes associated with the processes.

## Related software

This repository is a component of the **INGV pygeoapi processing platform**:

https://github.com/francescoingv/ingv-pygeoapi-processing-platform  
Platform DOI: https://doi.org/10.5281/zenodo.18892848

The pygeoapi plugins using this execution service are defined in:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins  
DOI: https://doi.org/10.5281/zenodo.18892819

pygeoapi plugins receive execution requests through the OGC API - Processes
APIs and forward the request to this service, which invokes the configured
application code.

------------------------------------------------------------------------

## Citation

If you use this software in scientific work, please cite it as:

Martinelli, F. (2026).  
*Generic processor provider for external execution services used by INGV pygeoapi process plugins*.  
DOI: https://doi.org/10.5281/zenodo.18892842

------------------------------------------------------------------------

## License

This project is distributed under the **MIT License**.

See the `LICENSE` file for details.

------------------------------------------------------------------------

## Authors

Francesco Martinelli  
Istituto Nazionale di Geofisica e Vulcanologia (INGV)  
Pisa, Italy
