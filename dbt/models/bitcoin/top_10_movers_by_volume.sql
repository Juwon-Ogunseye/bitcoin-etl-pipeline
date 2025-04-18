{{
  config(
    materialized='view'
  )
}}

WITH volume_calculations AS (
  SELECT
    from_address AS address,
    -wbtc_amount AS volume -- Negative for outflows
  FROM {{ source('bitcoin', 'erc20_transfers_wbtc') }}
  
  UNION ALL
  
  SELECT
    to_address AS address,
    wbtc_amount AS volume -- Positive for inflows
  FROM {{ source('bitcoin', 'erc20_transfers_wbtc') }}
),

net_volume AS (
  SELECT
    address,
    SUM(volume) AS net_volume,
    SUM(CASE WHEN volume > 0 THEN volume ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN volume < 0 THEN ABS(volume) ELSE 0 END) AS total_outflow,
    COUNT(*) AS transaction_count
  FROM volume_calculations
  GROUP BY address
),

ranked_volumes AS (
  SELECT
    address,
    net_volume,
    total_inflow,
    total_outflow,
    transaction_count,
    RANK() OVER (ORDER BY ABS(net_volume) DESC) AS volume_rank
  FROM net_volume
)

SELECT
  address,
  net_volume,
  total_inflow,
  total_outflow,
  transaction_count,
  volume_rank
FROM ranked_volumes
WHERE volume_rank <= 10
ORDER BY volume_rank