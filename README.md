# **🚀 WBTC → S3 → ClickHouse Analytics Pipeline**  
*High-performance blockchain ETL with etherium node, clichouse, S3, Airflow, DBT, and Metabase*  

### **🔍 Overview**  
This pipeline **extracts raw Ethereum data** (WBTC/Uniswap events) via **Chainlink RPC + Subgraph**, processes it with **Cryo**, stores in **S3**, loads into **ClickHouse**, transforms with **DBT**, and orchestrates with **Airflow**. Designed for high-throughput onchain analytics.  

---

## ⚡ Technology Stack  
### Programming Languages & Core Tools  
| **Category**       | **Technologies**                          |
|--------------------|------------------------------------------|
| **Blockchain**     | Rust (Cryo), Solidity (Subgraph contracts) |
| **Data Processing**| Python (Airflow, DBT), Jinja SQL (Templates) |
| **Database**       | ClickHouse SQL, PL/pgSQL (Metabase)      |
| **Infrastructure** | Docker, YAML, Bash                       |

---
---

## **⚡ Key Components**  
| **Layer**          | **Technology**                     | **Role**                                  |  
|---------------------|------------------------------------|-------------------------------------------|  
| **Ingestion**       | Chainlink RPC, Subgraph, Cryo      | Stream raw Ethereum logs/events           |  
| **Storage**         | S3 (Intermediate), ClickHouse      | Scalable raw data lake + analytics DB     |  
| **Transformation**  | DBT                                | Clean, aggregate, and model data          |  
| **Orchestration**   | Airflow                            | Schedule and monitor pipeline runs         |  
| **Visualization**   | Metabase                           | Interactive dashboards                    |  

---

## **🛠️ Architecture**  
graph LR  
  subgraph Docker Containers
    B[Cryo]
    C[Subgraph]
    D[Airflow]
    E[ClickHouse]
    F[Metabase]
  end
  
  A[Ethereum RPC] -->|Chainlink| B
  A -->|The Graph| C
  B -->|JSON| G[(S3 Bucket)]
  C -->|Decoded Events| G
  G -->|Trigger| D
  D -->|Load| E
  E -->|DBT| H[Analytics Models]
  H --> F

## **🚀 Quick Start**  
### **1. Prerequisites**  
- AWS credentials (for S3)  
- Chainlink RPC endpoint  
- Docker + Docker Compose  

### **2. Configure**  
```bash  
cp .env.example .env  # Set RPC_URL, S3_PATH, CLICKHOUSE_CREDS  
```  

### **3. Start Services**  
```bash  
docker-compose up -d --build  
```  
- **Airflow**: `http://localhost:8081` (DAGs: `eth_to_s3`, `s3_to_clickhouse`)  
- **Metabase**: `http://localhost:3000`  
- **ClickHouse**: Port `8123` (HTTP)  

### **4. Run Transformations**  
```bash  
docker exec -it dbt run-operation run_clickhouse_transforms  
```  

---

## **📊 Data Flow**  
1. **Extract**  
   - `cryo eth_logs --rpc <RPC_URL> --output s3://path/raw_logs.json`  
   - Subgraph listens for Uniswap/WBTC events  

2. **Load**  
   - Airflow DAGs parse JSON → S3 → ClickHouse (`eth_raw.logs`)  

3. **Transform**  
   - DBT models:  
     ```sql  
     -- models/wbtc_flows.sql  
     SELECT  
       from_address,  
       SUM(amount) as total_wbtc  
     FROM {{ ref('raw_ethereum_logs') }}  
     WHERE token = 'WBTC'  
     GROUP BY 1  
     ```  

4. **Visualize**  
   - Metabase connects to ClickHouse → Build dashboards  

---

## **📂 Repository Structure**  
```  
├── dags/                  # Airflow: eth_to_s3.py, s3_to_clickhouse.py  
├── dbt/                   # DBT models (staging, marts)  
│   ├── models/  
│   │   ├── staging/       # Raw schema tables  
│   │   └── marts/         # Analytics-ready models  
├── cryo_scripts/          # Cryo configs for Ethereum extraction  
├── docker/                # Custom images (Airflow + DBT)  
├── .env.example           # RPC, S3, and DB credentials  
└── docker-compose.yml     # Airflow, ClickHouse, Metabase  
```  

---

## **⚙️ Advanced Setup**  
### **Scaling Ingestion**  
- Parallelize Cryo jobs by block range:  
  ```python  
  # Airflow DAG to split into 10k-block chunks  
  for start_block in range(0, latest_block, 10_000):  
      cryo.extract(start_block, start_block+10_000)  
  ```  

---

## **📜 License**  
MIT License. *Not affiliated with Chainlink or Ethereum Foundation.*  

---

**💡 Need Help?**  
- For RPC issues: Check Chainlink node logs  
- For DBT errors: `docker logs dbt`  
- For Airflow: `docker-compose logs -f airflow-webserver`  

--- 