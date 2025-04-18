{{
  config(
    materialized='view'
  )
}}

SELECT 
    transaction_id AS tx_hash,
    transaction_timestamp AS timestamp,
    pair_token0_symbol,
    pair_token1_symbol,
    amount_u_s_d AS value_usd,
    amount0_in,
    amount1_in,
    amount0_out,
    amount1_out
FROM {{ source('bitcoin', 'swaps_latest') }}
