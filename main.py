import logging
from dags.subgraph_scripts.extract_subgraph_transfers import run_subgraph_job
from dags.cryo.crates.python.extract_cryo_erc20 import run_cryo_job
from dags.Load_Btc_Data.load_to_clickhouse import load_to_clickhouse
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_process.log'), 
        logging.StreamHandler() 
    ]
)


logging.info("ETL Process Started")

if __name__ == "__main__":
   
    logging.info("Starting Cryo Job...")
    try:
        run_cryo_job()
        logging.info("Cryo Job completed successfully.")
    except Exception as e:
        logging.error(f"Error in Cryo Job: {e}")
    
    logging.info("Starting Subgraph Job...")
    try:
        run_subgraph_job()
        logging.info("Subgraph Job completed successfully.")
    except Exception as e:
        logging.error(f"Error in Subgraph Job: {e}")
    
    logging.info("Starting Load to Clickhouse Job...")
    try:
        load_to_clickhouse()
        logging.info("Load to Clickhouse Job completed successfully.")
    except Exception as e:
        logging.error(f"Error in Load to Clickhouse Job: {e}")
    
    logging.info("ETL Process Completed")
