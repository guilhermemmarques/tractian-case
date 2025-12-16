# Take-Home Challenge: TracOS ↔ Client Integration Flow

## Introduction

This repository contains a technical assesment to evaluate your skills on a simulated scenario of an integration between Tractian's CMMS (TracOS) and a customer's ERP.

The test objective is to build an asynchronous Python service that simulates an integration between our CMMS (TracOS) and a customer's ERP software, containing both an inbound (client → TracOS) and outbound (TracOS → client) flows. The integration focus is to sync work orders between the systems.

The customer's system will be simulated by JSON files representing API responses. Our system will be represented by a MongoDB instance.

Create at least three modules: one to handle read/write on our system (TracOS), one to handle read/write on the customer's system and one to handle translations between systems. The main objective by creating these modules is to have a project where it is easy to add an integration to another system, without needing to modify the existing modules, only expanding them.

Notes: 
- The dependency management in this project must be done using Poetry.
- There is a docker-compose to create a MongoDB instance, figure out how to use it.
- There is a setup.py file that creates samples workorders on our system and on the customer's system (JSON file). You need to run this after you create the MongoDB instance with docker-compose. That file also has some tips on how to build your own code.

The main objectives of this assesment are to demonstrate:

- Clarity in functional requirements  
- Attention to expected system behavior  
- Code organization for future maintenance  

---

## What the System Must Do

1. **Inbound**  
   - Read JSON files (simulating the client's API response) from an input folder  
   - For each work order:  
     - Validate required fields (e.g., `id`, `status`, `createdAt`)  
     - Translate payload from client format → TracOS format  
     - Insert or update the record in a MongoDB collection  

2. **Outbound**  
   - Query MongoDB for work orders with `isSynced = false`  
   - For each record:  
     - Translate from TracOS format → client format  
     - Write the output JSON into an output folder, ready to "send" to the client  
     - Mark the document in MongoDB with `isSynced = true` and set a `syncedAt` timestamp  

3. **Translation / Normalization**  
   - Normalize date fields to UTC ISO 8601  
   - Map enums/status values (e.g., client uses `"NEW"`, TracOS uses `"created"`)  

4. **Resilience**  
   - Clear success and error logs without unreadable stack traces  
   - Handle I/O errors (corrupted file, permission issues) gracefully  
   - Simple retry or reconnect logic for MongoDB failures  

---

## Non-Technical Requirements

- **Complete README**: explain how to run and a summary of the chosen architecture
- **Configuration via environment variables**:  
  - `MONGO_URI` → MongoDB connection string  
  - `DATA_INBOUND_DIR` and `DATA_OUTBOUND_DIR` → input/output folders  
- **Basic tests**:  
  - Sample input and output JSON  
  - End-to-end workflow verification (full coverage not required)  
- **Best practices**: informative logging, readable code, simple modularity  

---

## Deliverables

1. Git repository forking this repository, containing:  
   - Running `main.py` should start the entire pipeline  
   - Clear modules for:  
     - Read/write on our system
     - Read/write on customer's system
     - Translating data between systems
2. Complete the `README.md` file with the folder structure and a general overview of how the system works.  
3. At least **one** automated test with `pytest` testing the end-to-end flow  

---
## Evaluation Criteria

- **Functionality**: inbound/outbound flows work as described  
- **Robustness**: proper error handling and logging  
- **Clarity**: self-explanatory, comprehensive README  
- **Maintainability**: clear separation of concerns, modular code  
- **Tests**: basic coverage of the main workflow  

---

## Setting Up The Project

### Important
This project was built using Python 3.11.14 on Linux Ubuntu. The commands provided are specific to this operating system. If you are using a different OS, please adjust the commands accordingly.

## Architecture Overview
The architecture of this project was designed with modularity, maintainability, and scalability in mind. Below is an overview of the key architectural decisions:

### 1. **Modularity**
The system is divided into distinct modules, each responsible for a specific part of the integration flow. This ensures that the code is easy to extend and maintain. The main modules are:
- **Inbound Module**: Handles reading and processing data from the client's system (JSON files).
- **Outbound Module**: Manages the extraction of data from TracOS and prepares it for the client's system.
- **Translation Module**: Contains the logic for translating and normalizing data between the two systems.

### 2. **Layered Design**
The project follows a layered design to separate concerns:
- **Models**: Define the data structures for both TracOS and the client's system.
- **Repositories**: Abstract the database operations (MongoDB) to ensure a clean separation between data access and business logic.
- **Services**: Implement the core business logic, such as validation, translation, and synchronization.
- **Modules**: Coordinate the overall workflows for inbound and outbound processes.

### 3. **Environment Configuration**
The system uses environment variables to configure key parameters, such as:
- MongoDB connection string (`MONGO_URI`).
- Input and output directories for JSON files (`DATA_INBOUND_DIR` and `DATA_OUTBOUND_DIR`).

This approach ensures flexibility and allows the system to adapt to different environments (e.g., development, testing, production).

### 4. **Error Handling and Logging**
The system is designed to handle errors gracefully, including:
- File I/O errors (e.g., missing or corrupted files).
- Database connection issues.
- Validation errors for incoming data.

Logs are implemented to provide clear and actionable information for debugging and monitoring.

### 5. **Scalability**
The modular design makes it easy to add support for new systems or workflows. For example:
- Adding a new client integration only requires implementing a new translation layer and extending the existing modules.
- The database layer is abstracted, allowing for future migration to other database systems if needed.

### 6. **Testability**
The architecture is designed to facilitate testing at multiple levels:
- Unit tests for individual components (e.g., models, services).
- Integration tests for workflows (e.g., inbound and outbound pipelines).
- End-to-end tests to verify the complete system behavior.

This ensures that the system is robust and behaves as expected under different scenarios.

### 7. **Resilience**
The system includes mechanisms to handle transient failures, such as retry logic for database operations and graceful handling of invalid data. This ensures that the integration flow remains reliable even in the face of unexpected issues.

By following these principles, the architecture ensures that the system is easy to understand, maintain, and extend, while meeting the functional requirements of the integration.

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Poetry for dependency management

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/guilhermemmarques/integrations-engineering-code-assesment.git
   cd integrations-engineering-code-assesment
   ```

2. **Install dependencies with Poetry**
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install dependencies
   poetry install
   ```

3. **Start MongoDB using Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run the setup script to initialize sample data**
   ```bash
   poetry run python setup.py
   ```

5. **Configure environment variables**
   ```bash
   # Create a .env file
   echo "MONGO_URI=mongodb://localhost:27017/tractian" > .env
   echo "DATA_INBOUND_DIR=./data/inbound" >> .env
   echo "DATA_OUTBOUND_DIR=./data/outbound" >> .env
   echo "MONGO_DATABASE=tractian" >> .env
   echo "MONGO_COLLECTION=workorders" >> .env

   # Or rename .env.example to .env
   mv .env.example .env
   ```

## Project Structure

```
tractian-case
├─ coverage.xml
├─ data
│  ├─ inbound
│  └─ outbound
├─ docker-compose.yml
├─ poetry.lock
├─ pyproject.toml
├─ pytest.ini
├─ README.md
├─ setup.py
└─ src
   ├─ conftest.py
   ├─ main.py
   ├─ models
   │  ├─ customer_models.py
   │  ├─ tests
   │  │  ├─ test_customer_models.py
   │  │  ├─ test_tracos_models.py
   │  ├─ tracOS_models.py
   │  ├─ __init__.py
   ├─ modules
   │  ├─ inbound.py
   │  ├─ outbound.py
   │  ├─ __init__.py
   ├─ repositories
   │  ├─ mongo
   │  │  ├─ mongo_workorder_repository.py
   │  │  ├─ __init__.py
   │  ├─ repository_factory.py
   │  ├─ tests
   │  │  ├─ test_repository_factory.py
   │  ├─ workorder_repository.py
   │  ├─ __init__.py
   ├─ service
   │  ├─ tests
   │  │  ├─ test_workorder_service.py
   │  ├─ workorder_service.py
   │  ├─ __init__.py
   ├─ tests
   │  ├─ test_end_to_end.py
   │  ├─ test_inbound_pipeline.py
   │  ├─ test_outbound_pipeline.py
   └─ __init__.py


```

## Running the Application

1. **Execute the main script**
   ```bash
   poetry run python src/main.py
   ```

## Testing

Run the tests with:
```bash
poetry run pytest
```

If you want to check the test coverage, run:
```bash
poetry run pytest --cov=src
```

This will display the coverage report for each file and the overall total. For example:
```
Name                                                   Stmts   Miss  Cover
--------------------------------------------------------------------------
src/__init__.py                                            0      0   100%
src/conftest.py                                           42      6    86%
src/main.py                                               32      5    84%
src/models/__init__.py                                     0      0   100%
src/models/customer_models.py                             16      0   100%
src/models/tests/test_customer_models.py                  23      0   100%
src/models/tests/test_tracos_models.py                    24      0   100%
src/models/tracOS_models.py                               22      0   100%
src/modules/__init__.py                                    0      0   100%
src/modules/inbound.py                                    55     18    67%
src/modules/outbound.py                                   47      8    83%
src/repositories/__init__.py                               0      0   100%
src/repositories/mongo/__init__.py                         0      0   100%
src/repositories/mongo/mongo_workorder_repository.py      41      7    83%
src/repositories/repository_factory.py                    13      3    77%
src/repositories/tests/test_repository_factory.py          4      0   100%
src/repositories/workorder_repository.py                   5      0   100%
src/service/__init__.py                                    0      0   100%
src/service/tests/test_workorder_service.py               50      0   100%
src/service/workorder_service.py                          29      0   100%
src/tests/test_end_to_end.py                              63      0   100%
src/tests/test_inbound_pipeline.py                        29      0   100%
src/tests/test_outbound_pipeline.py                       38      0   100%
--------------------------------------------------------------------------
TOTAL                                                    533     47    91%
```

Additionally, you can generate a `coverage.xml` file to visualize the test coverage in detail. By using tools like the Coverage Gutters extension in your code editor, you can see line-by-line coverage directly in your source files. This helps identify which parts of the code are covered by tests and which are not. Runs:
```bash
poetry run pytest --cov=src --cov-report=xml
```

## Troubleshooting

- **MongoDB Connection Issues**: Ensure Docker is running and the MongoDB container is up with `docker ps`
- **Missing Dependencies**: Verify Poetry environment is activated or run `poetry install` again
- **Permission Issues**: Check file permissions for data directories
- **Python Issue**: If you encounter the following error when running `main.py`:
```
ModuleNotFoundError: No module named 'src'
```

This issue occurs because the Python interpreter cannot locate the `src` module. To resolve this, you need to add the project's root directory to the `PYTHONPATH` environment variable. Run the following command from the root of the project:
```bash
PYTHONPATH=$(pwd) poetry run python src/main.py
```
This ensures that the Python interpreter includes the current project directory in its module search path, and the `main.py` run correctly
