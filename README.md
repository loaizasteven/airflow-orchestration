# Apache Airflow Local Development Setup

This repository contains a local Apache Airflow setup for development and testing.

## Getting Started

### Prerequisites

- uv installation `brew install uv`
- python 3.11 `uv venv --python 3.11`
- activate the virtual environment `source .venv/bin/activate`
- sync the dependencies `uv sync`

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
2. **Example DAG**: Check `dags/hello_world_dag.py` for a simple example
3. **Refresh DAGs**: If changes aren't visible, run:
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
│   ├── airflow.db            # SQLite database
│   └── logs/                 # Airflow logs
├── dags/                     # Your DAG files go here
├── logs/                     # Additional logs
├── plugins/                  # Custom plugins (if needed)
├── start_airflow.sh          # Manual start script (API server + scheduler)
├── start_airflow_standalone.sh # Standalone mode (recommended for local dev)
├── stop_airflow.sh           # Stop all Airflow processes
└── README.md                # This file
```

### Environment Variables

- `AIRFLOW_HOME`: Path to Airflow configuration and database files
- `AIRFLOW__CORE__DAGS_FOLDER`: Override DAGs folder location
- `AIRFLOW__CORE__LOAD_EXAMPLES`: Set to `False` to hide example DAGs

### Troubleshooting

- **Port conflicts**: Change the port in `start_airflow.sh` or use `--port` flag
- **Permission issues**: Ensure proper file permissions for the `airflow_home` directory
- **DAG not showing**: Check DAG syntax and refresh with `airflow dags reserialize`
- **Examples not showing**: Set `load_examples = True` in `airflow.cfg`.

## Clean up local db

Run the following command `airflow db clean --clean-before-timestamp "2025-07-01 00:00:00+01:00"`
then confirm with `delete rows`.