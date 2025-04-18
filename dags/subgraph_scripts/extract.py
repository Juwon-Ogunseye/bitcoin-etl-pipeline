import json
import os
import requests
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Constants
GRAPHQL_ENDPOINT = os.getenv("SUBGRAPH_URL")
QUERIES_DIR = 'Queries'
OUTPUT_DIR = 'output'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_graphql_query(query):
    """Execute a GraphQL query and return the response"""
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={'query': query},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        return None

def save_query_results(data, query_name):
    """Save query results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{query_name}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved results to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save results: {str(e)}")
        return None

def get_query_files():
    """Get all .graphql files from the queries directory"""
    if not os.path.exists(QUERIES_DIR):
        logger.error(f"Queries directory '{QUERIES_DIR}' not found")
        return []
    
    return [f for f in os.listdir(QUERIES_DIR) if f.endswith('.graphql')]

def process_query(query_file):
    """Process a single GraphQL query file"""
    query_path = os.path.join(QUERIES_DIR, query_file)
    query_name = os.path.splitext(query_file)[0]
    
    try:
        with open(query_path, 'r') as f:
            query = f.read()
        
        logger.info(f"Running query: {query_name}")
        result = run_graphql_query(query)
        
        if result and 'data' in result:
            save_query_results(result['data'], query_name)
        else:
            logger.error(f"No data returned for {query_name}")
            
    except Exception as e:
        logger.error(f"Error processing {query_file}: {str(e)}")

def main():
    """Main function to run all queries"""
    query_files = get_query_files()
    
    if not query_files:
        logger.error("No query files found")
        return
    
    logger.info(f"Found {len(query_files)} query files")
    
    for query_file in query_files:
        process_query(query_file)
    
    logger.info("All queries processed")

if __name__ == "__main__":
    main()