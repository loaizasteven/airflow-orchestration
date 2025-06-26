# Apache Airflow Local Development Setup

This repository contains a local Apache Airflow setup for development and testing with PostgreSQL database backend.

## Getting Started

### Prerequisites

- uv installation `brew install uv`
- python 3.11 `uv venv --python 3.11`
- activate the virtual environment `source .venv/bin/activate`
- sync the dependencies `uv sync`
- PostgreSQL 15+ `brew install postgresql@15`

### Database Setup

This setup uses **PostgreSQL** as the main database backend for Airflow metadata:

1. **Install and Start PostgreSQL**:
   ```bash
   brew install postgresql@15
   brew services start postgresql@15
   ```

2. **Create Airflow Database**:
   ```bash
   psql postgres
   CREATE DATABASE airflow_db;
   CREATE USER SLoaiza WITH PASSWORD 'airflow';
   GRANT ALL PRIVILEGES ON DATABASE airflow_db TO SLoaiza;
   \q
   ```

3. **Verify Connection**:
   ```bash
   psql -h localhost -U SLoaiza -d airflow_db
   ```

### Additional Providers

This setup includes additional Airflow providers for enhanced functionality:

- **PostgreSQL Provider**: For working with PostgreSQL databases
  ```bash
  uv pip install apache-airflow-providers-postgres
  ```

- **SQLite Provider**: For working with SQLite databases
  ```bash
  uv pip install apache-airflow-providers-sqlite
  ```

### Initial Setup

1. **Initialize Airflow Database** (first time setup)
   ```bash
   export AIRFLOW_HOME=$(pwd)/airflow_home
   airflow db migrate
   ```
   
   > **Note:** The `airflow.cfg` configuration file is included in the repository with optimal settings for local development. The database connection is configured for PostgreSQL at `postgresql://SLoaiza:airflow@localhost:5432/airflow_db`.

2. **Start Airflow Services**
   
   **Recommended (Simple):**
   ```bash
   ./start_airflow_standalone.sh
   ```
   
   **Alternative (Manual):**
   ```bash
   ./start_airflow.sh
   ```

3. **Access the Web UI**
   - Open http://localhost:8080 in your browser
   - **Login with auto-generated credentials:**
     - Username: `admin`
     - Password: Check [`credentials`](airflow_home/simple_auth_manager_passwords.json.generated) for the password

4. **Setup Database Connections** (Required for some DAGs)
   
   **PostgreSQL Connection for Data Pipeline:**
   ```bash
   # Create PostgreSQL connection for data processing
   airflow connections add 'postgres_connection' \
     --conn-type postgres \
     --conn-host localhost \
     --conn-port 5432 \
     --conn-login SLoaiza \
     --conn-password airflow \
     --conn-schema customers_db
   ```
   
   **SQLite Connection Example:**
   ```bash
   # Create a SQLite connection for data storage
   airflow connections add 'my_prod_database' \
     --conn-type sqlite \
     --conn-host './datasets/my_sqlite.db'
   ```
   
   **Via Web UI:**
   - Navigate to **Admin → Connections**
   - Click **Add Connection**
   - Fill in connection details

### Configuration File (airflow.cfg)

The Airflow configuration file is located at `airflow_home/airflow.cfg`. Key settings for local development:

- **DAGs Folder**: `dags/` - Put your DAG files here
- **Database**: PostgreSQL database at `postgresql://SLoaiza:airflow@localhost:5432/airflow_db`
- **Executor**: LocalExecutor (suitable for local development)
- **Web UI**: Runs on port 8080 by default
- **Authentication**: Simple auth manager with auto-generated admin password

#### Important Configuration Sections:

- `[core]` - Core Airflow settings including DAGs folder and executor
- `[webserver]` - Web UI configuration and security settings
- `[scheduler]` - Scheduler behavior and performance tuning
- `[database]` - PostgreSQL connection settings

### Working with DAGs

1. **Create DAGs**: Add Python files to the `dags/` directory

2. **Example DAGs**: Several example DAGs are included:
   - `hello_world_dag.py` - Simple hello world example
   - `custom.py` - Python task examples with pandas and sklearn
   - `custom_taskflow_dag.py` - Basic TaskFlow API with ETL pattern
   - `custom_xcom_dags.py` - XCom data passing using traditional PythonOperator
   - `custom_xcom_taskflow_dags.py` - XCom data passing using TaskFlow API
   - `sqllite_taskapi_dags.py` - SQLite data pipeline with TaskAPI
   - `branching_taskapi_dags.py` - Conditional branching examples
   - `postgres_pipeline_dags.py` - **Complete PostgreSQL data pipeline with SQL operations**

3. **TaskFlow API Examples**:
   - `custom_taskflow_dag.py`: Demonstrates modern TaskFlow API syntax with Extract-Transform-Load pattern
   - Automatic XCom handling through return values and function parameters
   - Clean, Pythonic DAG definition syntax

4. **XCom Data Passing Examples**:
   - `custom_xcom_dags.py`: Traditional approach using PythonOperator with manual XCom push/pull
     - Explicit `ti.xcom_push()` and `ti.xcom_pull()` operations
     - More verbose but gives fine-grained control over XCom keys
   - `custom_xcom_taskflow_dags.py`: Modern TaskFlow API with automatic XCom handling
     - Return values automatically become XComs
     - Function parameters automatically pull XCom values
     - Cleaner syntax with type hints and automatic data flow
   - Shows different patterns: single values, dictionaries, and multiple outputs
   - Demonstrates task dependencies and data flow between tasks

5. **PostgreSQL Data Pipeline DAG** (`postgres_pipeline_dags.py`):
   - **Complete SQL-based data processing pipeline**
   - Creates customer and purchase tables from SQL files
   - Inserts sample data using parameterized SQL queries
   - Performs table joins and data filtering
   - Exports filtered results to CSV files in `output/` directory
   - Demonstrates SQL templating and parameter passing
   - Uses SQL files from `sql_statements/` directory
   - Requires `postgres_connection` setup

6. **SQLite Data Pipeline DAG**: 
   - Reads CSV data from `datasets/car_data.csv`
   - Creates SQLite tables automatically
   - Inserts data using TaskAPI and SQLite hooks
   - Requires `my_prod_database` connection setup

7. **Refresh DAGs**: If changes aren't visible, run:
   ```bash
   airflow dags reserialize
   ```

### Stopping Airflow

```bash
pkill -f airflow
```

### Directory Structure

```
.
├── airflow_home/              # Airflow home directory
│   ├── airflow.cfg           # Main configuration file (PostgreSQL backend)
│   └── logs/                 # Airflow logs
├── dags/                     # Your DAG files go here
│   ├── hello_world_dag.py    # Simple example DAG
│   ├── custom.py             # Python task examples with pandas/sklearn
│   ├── custom_taskflow_dag.py # Basic TaskFlow API with ETL pattern
│   ├── custom_xcom_dags.py   # XCom data passing (PythonOperator)
│   ├── custom_xcom_taskflow_dags.py # XCom data passing (TaskFlow API)
│   ├── sqllite_taskapi_dags.py # SQLite data pipeline
│   ├── branching_taskapi_dags.py # Conditional branching examples
│   └── postgres_pipeline_dags.py # PostgreSQL data pipeline with SQL operations
├── datasets/                 # Data files for DAGs
│   ├── car_data.csv          # Sample car data
│   └── my_sqlite.db          # SQLite database for data storage
├── output/                   # Generated output files
│   ├── filtered_data.csv     # Filtered customer data from PostgreSQL pipeline
│   └── two_seaters.csv       # Filtered car data from other pipelines
├── sql_statements/           # SQL files for PostgreSQL pipeline
│   ├── create_table_customers.sql
│   ├── create_table_customer_purchases.sql
│   ├── insert_customers.sql
│   ├── insert_customer_purchases.sql
│   └── joining_table.sql
├── logs/                     # Additional logs
├── plugins/                  # Custom plugins (if needed)
├── start_airflow.sh          # Manual start script (API server + scheduler)
├── start_airflow_standalone.sh # Standalone mode (recommended for local dev)
├── stop_airflow.sh           # Stop all Airflow processes
└── README.md                # This file
```

### PostgreSQL Database Operations

The setup uses PostgreSQL for both Airflow metadata and data processing pipelines:

1. **Airflow Metadata Database**: `airflow_db`
   - Stores DAG runs, task instances, connections, etc.
   - Automatically managed by Airflow

2. **Data Processing Database**: `customers_db` (created by DAGs)
   - Used by PostgreSQL pipeline DAG for data processing
   - Created automatically by the postgres_pipeline_dags.py

#### Setup & Basic Commands

```bash
# Install and start PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create databases
psql -d postgres -c "CREATE DATABASE airflow_db;"
psql -d postgres -c "CREATE DATABASE customers_db;"

# Common commands
psql -d postgres -c "\l"                    # List databases
psql -d airflow_db -c "\dt"                 # List tables in airflow_db
psql -d customers_db -c "\dt"               # List tables in customers_db
psql -d postgres -c "\d table_name"         # Describe table
```

#### Airflow Integration

```bash
# Install provider
uv pip install apache-airflow-providers-postgres

# Create connection for data pipeline
airflow connections add 'postgres_connection' \
    --conn-type postgres \
    --conn-host localhost \
    --conn-port 5432 \
    --conn-login SLoaiza \
    --conn-password airflow \
    --conn-schema customers_db
```

#### Common SQL Operations

```sql
-- Basic table operations
CREATE TABLE employees (id SERIAL PRIMARY KEY, name VARCHAR(100), salary DECIMAL(10,2));
INSERT INTO employees (name, salary) VALUES ('John Doe', 75000.00);
SELECT * FROM employees WHERE salary > 50000;
UPDATE employees SET salary = salary * 1.1 WHERE dept = 'Engineering';

-- Advanced features
SELECT name, RANK() OVER (ORDER BY salary DESC) FROM employees;  -- Window functions
CREATE INDEX idx_employees_dept ON employees(dept);               -- Performance
```

#### Troubleshooting

```bash
# Check service status
brew services list | grep postgres

# Common fixes
psql -d postgres -c "CREATE DATABASE your_database;"  # Database doesn't exist
brew services restart postgresql@15                   # Connection issues
```

### SQLite Database Operations

The setup also includes SQLite databases for specific data processing tasks:

1. **Data Storage Database**: `datasets/my_sqlite.db`
   - Used by SQLite DAGs for data processing and storage
   - Created automatically by the SQLite data pipeline DAG

**Common SQLite Commands:**
```bash
# Connect to data storage database
sqlite3 datasets/my_sqlite.db

# View tables in database
.tables

# View table schema
.schema table_name

# Exit SQLite
.exit
```

### Environment Variables

- `AIRFLOW_HOME`: Path to Airflow configuration and database files
- `AIRFLOW__CORE__DAGS_FOLDER`: Override DAGs folder location
- `AIRFLOW__CORE__LOAD_EXAMPLES`: Set to `False` to hide example DAGs

### Troubleshooting

**Common Issues:**

- **Port conflicts**: Change the port in `start_airflow.sh` or use `--port` flag
- **Permission issues**: Ensure proper file permissions for the `airflow_home` directory
- **DAG not showing**: Check DAG syntax and refresh with `airflow dags reserialize`
- **Examples not showing**: Set `load_examples = True` in `airflow.cfg`

**Database Connection Issues:**
- **PostgreSQL connection failed**: Ensure PostgreSQL is running and credentials are correct
- **Database doesn't exist**: Create the required databases (`airflow_db`, `customers_db`)
- **Permission denied**: Grant proper privileges to the database user

**Airflow 3.0 Specific Issues:**

- **"Direct database access via ORM is not allowed"**: 
  - Don't use `settings.Session()` or direct database access in DAG files
  - Create connections via CLI or UI instead of programmatically

- **"Unknown hook type 'postgres'"**: 
  - Install the PostgreSQL provider: `uv pip install apache-airflow-providers-postgres`
  - Restart Airflow after installing new providers

- **"Unknown hook type 'sqlite'"**: 
  - Install the SQLite provider: `uv pip install apache-airflow-providers-sqlite`
  - Restart Airflow after installing new providers

- **"No module named 'airflow.providers.postgres'"**: 
  - Ensure PostgreSQL provider is installed in the correct virtual environment
  - Import provider modules inside task functions, not at module level
  - Restart Airflow services to pick up new providers

**Provider Installation:**
```bash
# Install PostgreSQL provider
uv pip install apache-airflow-providers-postgres

# Install SQLite provider
uv pip install apache-airflow-providers-sqlite

# Verify installation
uv pip list | grep -E "(postgres|sqlite)"
airflow providers list | grep -iE "(postgres|sqlite)"

# Restart Airflow after installing new providers
pkill -f airflow
./start_airflow_standalone.sh
```

**Connection Issues:**
```bash
# List all connections
airflow connections list

# Add PostgreSQL connection
airflow connections add 'postgres_connection' \
  --conn-type postgres \
  --conn-host localhost \
  --conn-port 5432 \
  --conn-login SLoaiza \
  --conn-password airflow \
  --conn-schema customers_db

# Add SQLite connection
airflow connections add 'my_prod_database' \
  --conn-type sqlite \
  --conn-host './datasets/my_sqlite.db'

# Delete connection if needed
airflow connections delete 'connection_name'
```

**macOS Compatibility Issues:**

If you encounter segmentation faults (SIGSEGV) on macOS, this is a known issue due to macOS limitations with process forking and network proxy queries. Here's how to resolve it:

- **Immediate Fix** (for current terminal session):
  ```bash
  export PYTHONFAULTHANDLER=true
  export no_proxy='*'
  ```

- **Permanent Fix** (add to your `~/.zshrc`):
  ```bash
  echo 'export PYTHONFAULTHANDLER=true' >> ~/.zshrc
  echo 'export no_proxy="*"' >> ~/.zshrc
  source ~/.zshrc
  ```

- **Alternative Solution**: Use Docker for Airflow on macOS:
  ```bash
  # Docker is the most reliable approach for running Airflow on macOS
  docker-compose up -d
  ```

**Note**: Only Linux-based distributions are officially supported as "Production" execution environments for Airflow. macOS is suitable for development but may encounter compatibility issues.

## Data Pipeline Examples

### PostgreSQL Pipeline (`postgres_pipeline_dags.py`)

This DAG demonstrates a complete data processing pipeline using PostgreSQL:

1. **Table Creation**: Creates `customers` and `customer_purchases` tables
2. **Data Insertion**: Inserts sample customer and purchase data
3. **Data Processing**: Joins tables and creates a complete customer details view
4. **Data Filtering**: Filters data based on price ranges using parameterized queries
5. **Data Export**: Exports filtered results to CSV files in the `output/` directory

**Key Features:**
- Uses SQL files from `sql_statements/` directory for better organization
- Demonstrates parameterized SQL queries for dynamic filtering
- Shows proper task dependencies and data flow
- Outputs results to CSV files for further analysis

### SQLite Pipeline (`sqllite_taskapi_dags.py`)

This DAG demonstrates working with SQLite databases:

1. **Data Ingestion**: Reads CSV data from `datasets/car_data.csv`
2. **Database Operations**: Creates tables and inserts data into SQLite
3. **Data Processing**: Filters and processes car data
4. **Output Generation**: Creates filtered datasets like `two_seaters.csv`

## Clean up local db

Run the following command `airflow db clean --clean-before-timestamp "2025-07-01 00:00:00+01:00"`
then confirm with `delete rows`.