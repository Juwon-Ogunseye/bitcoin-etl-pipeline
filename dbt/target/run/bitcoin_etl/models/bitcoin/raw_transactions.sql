

  create view `bitcoin`.`raw_transactions__dbt_tmp` 
  
    
    
  as (
    

SELECT 
    transaction_id AS tx_hash,
    transaction_timestamp AS timestamp,
    amount_u_s_d AS value_usd,
    pair_token0_symbol || '/' || pair_token1_symbol AS trading_pair
FROM `bitcoin`.`swaps_latest`
LIMIT 1000
  )