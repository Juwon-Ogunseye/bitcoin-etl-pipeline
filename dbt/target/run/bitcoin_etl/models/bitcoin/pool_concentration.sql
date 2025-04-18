

  create view `bitcoin`.`pool_concentration` 
  
    
    
  as (
    

SELECT
  pair_token0_symbol || '-' || pair_token1_symbol AS pair_name,
  liquidity_token_balance,
  liquidity_token_balance / SUM(liquidity_token_balance) OVER () AS overall_share_pct,
  CASE
    WHEN liquidity_token_balance > 1000 THEN 'Whale'
    WHEN liquidity_token_balance > 100 THEN 'Dolphin'
    ELSE 'Minnow'
  END AS provider_size
FROM `bitcoin`.`liquidity_positions_largest`
ORDER BY liquidity_token_balance DESC
  )