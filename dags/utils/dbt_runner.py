import subprocess
import os
import logging

def run_dbt_models():
    dbt_path = "/opt/airflow/dbt"
    try:
        # Test connection first
        debug = subprocess.run(
            ["dbt", "debug", "--project-dir", dbt_path],
            capture_output=True,
            text=True
        )
        print(debug.stdout)  # Print full debug output
        if debug.returncode != 0:
            raise RuntimeError(f"Connection failed:\n{debug.stderr}")
            
        # Run models
        result = subprocess.run(
            ["dbt", "run", "--project-dir", dbt_path],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(f"Model run failed:\n{result.stderr}")
            
        return "Success"
    except Exception as e:
        raise RuntimeError(f"DBT Error: {str(e)}")