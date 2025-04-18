from web3 import Web3
from datetime import timedelta 
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import logging
import sys
import cryo
import os
sys.path.append('/opt/airflow')
sys.path.append('/opt/airflow/cryo')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from airflow.configuration import conf

# Set this at the top of your DAG file
log_folder = conf.get('logging', 'BASE_LOG_FOLDER')
# Import custom functions
# For scripts in dags/subgraph_scripts/
#from subgraph_scripts.extract_subgraph_transfers import run_subgraph_job
from dags.subgraph_scripts.extract_subgraph_transfers import run_subgraph_job
from dags.cryo.crates.python.extract_cryo_erc20 import run_cryo_job
from dags.Load_Btc_Data.load_to_clickhouse import load_to_clickhouse
#from bitcoin_etl_pipeline.Load_Btc_Data.load_to_clickhouse import load_to_clickhouse
from dags.utils.dbt_runner import run_dbt_models


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/airflow/logs/etl_process.log'),
        logging.StreamHandler()
    ]
)

# # Define default arguments for the DAG
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
# }
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,  # Increased from 1
    'retry_delay': timedelta(minutes=5),  # Added retry delay
}

# Define the DAG
with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="A DAG to extract data using Cryo and Subgraph, and load it into ClickHouse",
    schedule_interval="@daily",  # Run daily
    start_date=days_ago(1),     # Start from one day ago
    catchup=False,              # Do not backfill past runs
) as dag:

    # Task 1: Run Cryo Job
    cryo_task = PythonOperator(
        task_id="run_cryo_job",
        python_callable=run_cryo_job,
        provide_context=True,
    )

    # Task 2: Run Subgraph Job
    subgraph_task = PythonOperator(
        task_id="run_subgraph_job",
        python_callable=run_subgraph_job,
        provide_context=True,
    )

    # Task 3: Load Data to ClickHouse
    load_task = PythonOperator(
        task_id="load_to_clickhouse",
        python_callable=load_to_clickhouse,
        provide_context=True,
    )
    #task 4: Load Data to DBT
    dbt_run = PythonOperator(
    task_id="run_dbt_models",
    python_callable=run_dbt_models,
    provide_context=True,
    dag=dag
    )
    # Define task dependencies
    cryo_task >> subgraph_task >> load_task >> dbt_run