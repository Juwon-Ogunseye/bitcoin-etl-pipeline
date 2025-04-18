from web3 import Web3
import cryo
import os
import json
import pandas as pd
import boto3
from dotenv import load_dotenv
import cryo
import os
import json
import pandas as pd
import boto3
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_cryo_job():
    try:
        # Load environment variables
        load_dotenv()
        eth_rpc = os.getenv("ETH_RPC")
        
        if not eth_rpc:
            raise ValueError("ETH_RPC environment variable not set")
        
        web3 = Web3(Web3.HTTPProvider(
            eth_rpc,
            request_kwargs={'timeout': 60} 
        ))
        
        logger.info(f"Connecting to Ethereum RPC at: {eth_rpc}")
        
        if not web3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum RPC")
        
        logger.info("Ethereum RPC connected successfully")
        
        # Define block range with error handling
        try:
            block = web3.eth.block_number
            latest = block - 7200
            block_range = f"{latest - 300}:{latest}"
            logger.info(f"Processing blocks: {block_range}")
        except Exception as e:
            raise ValueError(f"Failed to get block number: {str(e)}")

        # WBTC contract address
        contract_address = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'

        logger.info("Starting Cryo data collection...")
        data = cryo.collect(
            "erc20_transfers",
            blocks=[block_range],
            contract=[contract_address],
            rpc=eth_rpc,
            output_format="pandas",
            hex=True,
            requests_per_second=25
        )

        # Process data
        data['wbtc_amount'] = data['value_f64'] / 1e8
        ndjson_data = data.to_dict(orient="records")
        ndjson_lines = "\n".join(json.dumps(record) for record in ndjson_data)

        # Upload to S3
        logger.info("Uploading to S3...")
        s3 = boto3.client('s3',
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

        response = s3.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key="erc20_transfers_wbtc.ndjson",
            Body=ndjson_lines,
            ContentType="application/x-ndjson"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info("✅ Upload complete")
        else:
            raise Exception(f"S3 upload failed: {response}")

    except Exception as e:
        logger.error(f"Error in run_cryo_job: {str(e)}")
        raise 