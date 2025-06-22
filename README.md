# Apache Airflow Local Development Setup

This repository contains a local Apache Airflow setup for development and testing.

## Getting Started

### Prerequisites

- uv installation `brew install uv`
- python 3.11 `uv venv --python 3.11`
- activate the virtual environment `source .venv/bin/activate`
- sync the dependencies `uv sync`

### Additional Providers

This setup includes additional Airflow providers for enhanced functionality:

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
   
   > **Note:** The `airflow.cfg` configuration file is included in the repository with optimal settings for local development. The database and logs are generated locally and not tracked in git. You'll need to update the `dags_folder` in [airflow.cfg](./airflow_home/airflow.cfg) file.

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

4. **Setup Database Connections** (Optional)
   
   For DAGs that use external databases, create connections via CLI or UI:
   
   **SQLite Connection Example:**
   ```bash
   # Create a SQLite connection for data storage
   airflow connections add 'my_prod_database' \
     --conn-type sqlite \
     --conn-host '/path/to/your/database.db'
   ```
   
   **Via Web UI:**
   - Navigate to **Admin → Connections**
   - Click **Add Connection**
   - Fill in connection details

### Configuration File (airflow.cfg)

The Airflow configuration file is located at `airflow_home/airflow.cfg`. Key settings for local development:

- **DAGs Folder**: `dags/` - Put your DAG files here
- **Database**: SQLite database at `airflow_home/airflow.db`
- **Executor**: LocalExecutor (suitable for local development)
- **Web UI**: Runs on port 8080 by default
- **Authentication**: Simple auth manager with auto-generated admin password

#### Important Configuration Sections:

- `[core]` - Core Airflow settings including DAGs folder and executor
- `[webserver]` - Web UI configuration and security settings
- `[scheduler]` - Scheduler behavior and performance tuning
- `[database]` - Database connection settings

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

5. **SQLite Data Pipeline DAG**: 
   - Reads CSV data from `datasets/car_data.csv`
   - Creates SQLite tables automatically
   - Inserts data using TaskAPI and SQLite hooks
   - Requires `my_prod_database` connection setup

6. **Refresh DAGs**: If changes aren't visible, run:
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
│   ├── airflow.cfg           # Main configuration file
│   ├── airflow.db            # SQLite database (Airflow metadata)
│   └── logs/                 # Airflow logs
├── dags/                     # Your DAG files go here
│   ├── hello_world_dag.py    # Simple example DAG
│   ├── custom.py             # Python task examples with pandas/sklearn
│   ├── custom_taskflow_dag.py # Basic TaskFlow API with ETL pattern
│   ├── custom_xcom_dags.py   # XCom data passing (PythonOperator)
│   ├── custom_xcom_taskflow_dags.py # XCom data passing (TaskFlow API)
│   ├── sqllite_taskapi_dags.py # SQLite data pipeline
│   └── branching_taskapi_dags.py # Conditional branching examples
├── datasets/                 # Data files for DAGs
│   ├── car_data.csv          # Sample car data
│   └── my_sqlite.db          # SQLite database for data storage
├── logs/                     # Additional logs
├── plugins/                  # Custom plugins (if needed)
├── start_airflow.sh          # Manual start script (API server + scheduler)
├── start_airflow_standalone.sh # Standalone mode (recommended for local dev)
├── stop_airflow.sh           # Stop all Airflow processes
└── README.md                # This file
```

### SQLite Database Operations

The setup includes SQLite databases for both Airflow metadata and data storage:

1. **Airflow Metadata Database**: `airflow_home/airflow.db`
   - Stores DAG runs, task instances, connections, etc.
   - Automatically managed by Airflow

2. **Data Storage Database**: `datasets/my_sqlite.db`
   - Used by DAGs for data processing and storage
   - Created automatically by the SQLite data pipeline DAG

**Common SQLite Commands:**
```bash
# Connect to Airflow metadata database
sqlite3 airflow_home/airflow.db

# Connect to data storage database
sqlite3 datasets/my_sqlite.db

# View tables in database
.tables

# View table schema
.schema table_name

# Exit SQLite
.exit
```

### PostgreSQL Database Operations

#### Setup & Basic Commands

```bash
# Install and start PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create user database (optional)
psql -d postgres -c "CREATE DATABASE \"$(whoami)\";"

# Common commands
psql -d postgres -c "\l"                    # List databases
psql -d postgres -c "\dt"                   # List tables
psql -d postgres -c "\d table_name"         # Describe table
psql -d postgres -c "CREATE DATABASE mydb;" # Create database
```

#### Airflow Integration

```bash
# Install provider
uv pip install apache-airflow-providers-postgres

# Create connection
airflow connections add 'postgres_default' \
    --conn-type postgres \
    --conn-host localhost \
    --conn-port 5432 \
    --conn-login postgres \
    --conn-password your_password \
    --conn-schema your_database
```

**Example DAG:**
```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from datetime import datetime, timedelta

dag = DAG('postgres_example', start_date=datetime(2024, 1, 1), schedule=timedelta(days=1))

create_table = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql="CREATE TABLE IF NOT EXISTS employees (id SERIAL PRIMARY KEY, name VARCHAR(100), dept VARCHAR(50));",
    dag=dag
)

@task
def query_data():
    hook = PostgresHook(postgres_conn_id='postgres_default')
    return hook.get_records("SELECT * FROM employees;")

create_table >> query_data()
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

**Airflow 3.0 Specific Issues:**

- **"Direct database access via ORM is not allowed"**: 
  - Don't use `settings.Session()` or direct database access in DAG files
  - Create connections via CLI or UI instead of programmatically

- **"Unknown hook type 'sqlite'"**: 
  - Install the SQLite provider: `uv pip install apache-airflow-providers-sqlite`
  - Restart Airflow after installing new providers

- **"No module named 'airflow.providers.sqlite'"**: 
  - Ensure SQLite provider is installed in the correct virtual environment
  - Import provider modules inside task functions, not at module level
  - Restart Airflow services to pick up new providers

**Provider Installation:**
```bash
# Install SQLite provider
uv pip install apache-airflow-providers-sqlite

# Verify installation
uv pip list | grep sqlite
airflow providers list | grep -i sqlite

# Restart Airflow after installing new providers
pkill -f airflow
./start_airflow_standalone.sh
```

**Connection Issues:**
```bash
# List all connections
airflow connections list

# Add SQLite connection
airflow connections add 'my_prod_database' \
  --conn-type sqlite \
  --conn-host '/path/to/database.db'

# Delete connection if needed
airflow connections delete 'my_prod_database'
```

## Clean up local db

Run the following command `airflow db clean --clean-before-timestamp "2025-07-01 00:00:00+01:00"`
then confirm with `delete rows`.