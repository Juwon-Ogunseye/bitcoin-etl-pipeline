# import json
# import time
# import requests
# import sys
# import re
# import boto3
# from datetime import datetime
# from dotenv import load_dotenv
# import logging
# import os

# # Load environment variables
# load_dotenv()

# # === Constants ===
# GRAPHQL_ENDPOINT = os.getenv("SUBGRAPH_URL")
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
# QUERIES_DIR = 'Queries'
# LOGS_DIR = 'Logs'
# OUTPUTS_DIR = 'Outputs'

# # Set the new timeout duration (e.g., 60 seconds)
# TIMEOUT_DURATION = 60  # Increased timeout from 40 to 60 seconds

# # === Setup Logging ===
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)

# log_filename = os.path.join(LOGS_DIR, f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log")

# logger = logging.getLogger("GraphQLExecutor")
# logger.setLevel(logging.DEBUG)

# file_handler = logging.FileHandler(log_filename)
# file_handler.setLevel(logging.DEBUG)

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.addHandler(console_handler)

# # === Flattening Utils ===
# def to_snake_case(s):
#     return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

# def to_camel_case(s):
#     parts = s.split('_')
#     return parts[0] + ''.join(word.capitalize() for word in parts[1:])

# def convert_special_fields(key, value):
#     if key in [
#         "derivedETH", "ethPrice", "amountUSD", "amount1Out", "amount0Out", 
#         "liquidityTokenTotalSupply", "liquidityTokenBalance", "reserveUSD", 
#         "reserveETH", "amount0In", "amount1In", "daily_volume_u_s_d", 
#         "daily_txns", "daily_volume_token0", "daily_volume_token1", 
#         "hourly_volume_token0", "hourly_volume_token1", "hourly_volume_u_s_d", 
#         "hourly_txns", "dailyVolumeUSD", "dailyTxns", "dailyVolumeToken0", 
#         "dailyVolumeToken1", "hourlyVolumeToken0", "hourlyVolumeToken1",
#         "hourlyVolumeUSD","hourlyTxns", "daily_volume_e_t_h",
#         "daily_volume_u_s_d","total_liquidity_e_t_h", "total_liquidity_u_s_d",
#         "dailyVolumeETH", "dailyVolumeUSD","totalLiquidityETH", "totalLiquidityUSD"
#     ]:
#         try:
#             return float(value)
#         except ValueError:
#             return value
#     if key in ["timestamp", "createdAtTimestamp", "date", "hour_start_unix", "hourStartUnix"]:
#         try:
#             return datetime.utcfromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
#         except (ValueError, TypeError):
#             return value
#     return value

# def flatten_json(y, parent_key='', sep='_', case='snake'):
#     items = []
#     for k, v in y.items():
#         new_key = f"{parent_key}{sep}{k}" if parent_key else k
#         new_key = to_snake_case(new_key) if case == 'snake' else to_camel_case(new_key)
#         if isinstance(v, dict):
#             items.extend(flatten_json(v, new_key, sep=sep, case=case).items())
#         else:
#             items.append((new_key, convert_special_fields(k, v)))
#     return dict(items)

# def flatten_all_objects(data, case='snake'):
#     if isinstance(data, dict):
#         return {
#             k: flatten_all_objects(v, case=case) if isinstance(v, (dict, list)) else convert_special_fields(k, v)
#             for k, v in data.items()
#         }
#     elif isinstance(data, list):
#         return [flatten_json(item, case=case) if isinstance(item, dict) else item for item in data]
#     return data

# # === S3 Upload (NDJSON) ===
# def upload_to_s3_ndjson(data, key):
#     s3 = boto3.client('s3', region_name=AWS_REGION)
#     try:
#         if not isinstance(data, list):
#             data = [data]

#         ndjson_data = "\n".join([json.dumps(item) for item in data])
#         logger.debug(f"NDJSON data (first 500 characters): {ndjson_data[:500]}")

#         s3.put_object(Bucket=S3_BUCKET_NAME, Key=key, Body=ndjson_data)
#         logger.info(f"🪣 Uploaded to S3 in NDJSON format: s3://{S3_BUCKET_NAME}/{key}")
#     except Exception as e:
#         logger.error(f"❌ S3 upload failed: {str(e)[:200]}...")  # Shorten long error messages

# # === Save Output Locally ===
# def save_output_locally(data, key):
#     if not os.path.exists(OUTPUTS_DIR):
#         os.makedirs(OUTPUTS_DIR)
    
#     output_filename = os.path.join(OUTPUTS_DIR, f"{key}.json")
#     with open(output_filename, 'w') as outfile:
#         json.dump(data, outfile, indent=2)
    
#     logger.info(f"📂 Output saved locally: {output_filename}")

# # === Main Query Execution ===
# def execute_query(query_file, case='snake'):
#     query_path = os.path.join(QUERIES_DIR, query_file)
#     s3_key = f"{query_file.replace('.graphql', '')}.ndjson"
#     local_output_key = query_file.replace('.graphql', '')

#     logger.info(f"📄 Running query: {query_file}")
#     try:
#         with open(query_path, 'r') as file:
#             query = file.read()

#         start_time = time.time()
#         response = requests.post(GRAPHQL_ENDPOINT, json={'query': query}, timeout=TIMEOUT_DURATION)
#         elapsed_time = time.time() - start_time

#         result_json = response.json()

#         if 'data' in result_json:
#             flattened = {
#                 key: flatten_all_objects(value, case=case)
#                 for key, value in result_json['data'].items()
#             }
#             result_json['data'] = flattened

#             first_key = next(iter(result_json['data']))
#             data_to_upload = result_json['data'][first_key]

#             # Handle case where the data is a dictionary, not a list
#             if isinstance(data_to_upload, dict):
#                 data_to_upload = [data_to_upload]  # Convert dictionary to a list of objects

#             if isinstance(data_to_upload, list):
#                 logger.debug(f"Flattened Data (first 2 items): {json.dumps(data_to_upload[:2], indent=2)[:500]}")

#                 # Save locally
#                 save_output_locally(data_to_upload, local_output_key)

#                 # Upload to S3
#                 upload_to_s3_ndjson(data_to_upload, s3_key)
#             else:
#                 logger.warning(f"❌ No list data to upload for {query_file}. Data format: {type(data_to_upload)}")

#         logger.info(f"✅ Query {query_file} finished in {elapsed_time:.2f}s")
#         logger.debug(json.dumps(result_json, indent=2)[:5000])

#     except requests.exceptions.Timeout:
#         logger.error(f"❌ Query {query_file} timed out after {TIMEOUT_DURATION} seconds.")
#     except Exception as e:
#         logger.exception(f"❌ Failed to execute {query_file}: {e}")

# # === Main Entry Point ===
# def main():
#     case = 'snake'
#     query_files = []

#     # Check for command-line arguments to override the default case or add specific query files
#     for arg in sys.argv[1:]:
#         if arg.startswith('--case='):
#             case = arg.split('=')[1].lower()
#         else:
#             if not arg.endswith('.graphql'):
#                 arg += '.graphql'
#             query_files.append(arg)

#     # Check if the Queries directory exists
#     if not os.path.exists(QUERIES_DIR):
#         logger.error(f"❌ Queries directory '{QUERIES_DIR}' does not exist.")
#         return

#     # Get all GraphQL files in the Queries directory
#     all_query_files = [file for file in os.listdir(QUERIES_DIR) if file.endswith('.graphql')]

#     # Check if there are exactly 16 query files
#     if len(all_query_files) != 16:
#         logger.error(f"❌ There are {len(all_query_files)} query files in the 'Queries' directory, but exactly 16 are required.")
#         return

#     logger.info(f"📦 Found {len(all_query_files)} query files in 'Queries' directory, proceeding to run them...")

#     # If specific query files are passed as arguments, execute only those
#     if query_files:
#         for query_file in query_files:
#             execute_query(query_file, case=case)
#     else:
#         logger.info("📦 No query file provided. Running all GraphQL files in 'Queries' directory...")
#         for query_file in all_query_files:
#             execute_query(query_file, case=case)

# if __name__ == "__main__":
#     main()
import json
import time
import requests
import sys
import re
import boto3
from datetime import datetime
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# === Constants ===
GRAPHQL_ENDPOINT = os.getenv("SUBGRAPH_URL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
QUERIES_DIR = 'Queries'
LOGS_DIR = 'Logs'
OUTPUTS_DIR = 'Outputs'


TIMEOUT_DURATION = 60  

# === Setup Logging ===
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

log_filename = os.path.join(LOGS_DIR, f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log")

logger = logging.getLogger("GraphQLExecutor")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# === Flattening Utils ===
def to_snake_case(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def to_camel_case(s):
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def convert_special_fields(key, value):
    if key in [
        "derivedETH", "ethPrice", "amountUSD", "amount1Out", "amount0Out", 
        "liquidityTokenTotalSupply", "liquidityTokenBalance", "reserveUSD", 
        "reserveETH", "amount0In", "amount1In", "daily_volume_u_s_d", 
        "daily_txns", "daily_volume_token0", "daily_volume_token1", 
        "hourly_volume_token0", "hourly_volume_token1", "hourly_volume_u_s_d", 
        "hourly_txns", "dailyVolumeUSD", "dailyTxns", "dailyVolumeToken0", 
        "dailyVolumeToken1", "hourlyVolumeToken0", "hourlyVolumeToken1",
        "hourlyVolumeUSD","hourlyTxns", "daily_volume_e_t_h",
        "daily_volume_u_s_d","total_liquidity_e_t_h", "total_liquidity_u_s_d",
        "dailyVolumeETH", "dailyVolumeUSD","totalLiquidityETH", "totalLiquidityUSD"
    ]:
        try:
            return float(value)
        except ValueError:
            return value
    if key in ["timestamp", "createdAtTimestamp", "date", "hour_start_unix", "hourStartUnix"]:
        try:
            return datetime.utcfromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return value
    return value

def flatten_json(y, parent_key='', sep='_', case='snake'):
    items = []
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        new_key = to_snake_case(new_key) if case == 'snake' else to_camel_case(new_key)
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep, case=case).items())
        else:
            items.append((new_key, convert_special_fields(k, v)))
    return dict(items)

def flatten_all_objects(data, case='snake'):
    if isinstance(data, dict):
        return {
            k: flatten_all_objects(v, case=case) if isinstance(v, (dict, list)) else convert_special_fields(k, v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [flatten_json(item, case=case) if isinstance(item, dict) else item for item in data]
    return data

# S3 Upload (NDJSON) 
def upload_to_s3_ndjson(data, key):
    s3 = boto3.client('s3', region_name=AWS_REGION)
    try:
        if not isinstance(data, list):
            data = [data]

        ndjson_data = "\n".join([json.dumps(item) for item in data])
        logger.debug(f"NDJSON data (first 500 characters): {ndjson_data[:500]}")

        s3.put_object(Bucket=S3_BUCKET_NAME, Key=key, Body=ndjson_data)
        logger.info(f"🪣 Uploaded to S3 in NDJSON format: s3://{S3_BUCKET_NAME}/{key}")
    except Exception as e:
        logger.error(f"❌ S3 upload failed: {str(e)[:200]}...")  # Shorten long error messages

def save_output_locally(data, key):
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)
    
    output_filename = os.path.join(OUTPUTS_DIR, f"{key}.json")
    with open(output_filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)
    
    logger.info(f"📂 Output saved locally: {output_filename}")

# === Main Query Execution ===
def execute_query(query_file, case='snake'):
    query_path = os.path.join(QUERIES_DIR, query_file)
    s3_key = f"{query_file.replace('.graphql', '')}.ndjson"
    local_output_key = query_file.replace('.graphql', '')

    logger.info(f"📄 Running query: {query_file}")
    try:
        with open(query_path, 'r') as file:
            query = file.read()

        start_time = time.time()
        response = requests.post(GRAPHQL_ENDPOINT, json={'query': query}, timeout=TIMEOUT_DURATION)
        elapsed_time = time.time() - start_time

        result_json = response.json()

        if 'data' in result_json:
            flattened = {
                key: flatten_all_objects(value, case=case)
                for key, value in result_json['data'].items()
            }
            result_json['data'] = flattened

            first_key = next(iter(result_json['data']))
            data_to_upload = result_json['data'][first_key]

            # Handle case where the data is a dictionary, not a list
            if isinstance(data_to_upload, dict):
                data_to_upload = [data_to_upload]  
            if isinstance(data_to_upload, list):
                logger.debug(f"Flattened Data (first 2 items): {json.dumps(data_to_upload[:2], indent=2)[:500]}")

                # Save locally
                save_output_locally(data_to_upload, local_output_key)

                # Upload to S3
                upload_to_s3_ndjson(data_to_upload, s3_key)
            else:
                logger.warning(f"❌ No list data to upload for {query_file}. Data format: {type(data_to_upload)}")

        logger.info(f"✅ Query {query_file} finished in {elapsed_time:.2f}s")
        logger.debug(json.dumps(result_json, indent=2)[:5000])

    except requests.exceptions.Timeout:
        logger.error(f"❌ Query {query_file} timed out after {TIMEOUT_DURATION} seconds.")
    except Exception as e:
        logger.exception(f"❌ Failed to execute {query_file}: {e}")

# === Wrapper Function ===
def run_subgraph_job():
    case = 'snake'
    query_files = []

    # Check for command-line arguments to override the default case or add specific query files
    for arg in sys.argv[1:]:
        if arg.startswith('--case='):
            case = arg.split('=')[1].lower()
        else:
            if not arg.endswith('.graphql'):
                arg += '.graphql'
            query_files.append(arg)

    # Check if the Queries directory exists
    if not os.path.exists(QUERIES_DIR):
        logger.error(f"❌ Queries directory '{QUERIES_DIR}' does not exist.")
        return

    # Get all GraphQL files in the Queries directory
    all_query_files = [file for file in os.listdir(QUERIES_DIR) if file.endswith('.graphql')]

    # Check if there are exactly 16 query files
    if len(all_query_files) != 16:
        logger.error(f"❌ There are {len(all_query_files)} query files in the 'Queries' directory, but exactly 16 are required.")
        return

    logger.info(f"📦 Found {len(all_query_files)} query files in 'Queries' directory, proceeding to run them...")

    # If specific query files are passed as arguments, execute only those
    if query_files:
        for query_file in query_files:
            execute_query(query_file, case=case)
    else:
        logger.info("📦 No query file provided. Running all GraphQL files in 'Queries' directory...")
        for query_file in all_query_files:
            execute_query(query_file, case=case)

if __name__ == "__main__":
    run_subgraph_job()
