

  create view `bitcoin`.`top_liquidity_providers__dbt_tmp` 
  
    
    
  as (
    

WITH pool_stats AS (
  SELECT
    pair_id,
    pair_token0_symbol || '-' || pair_token1_symbol AS pair_name,
    COUNT(DISTINCT user_id) AS unique_providers,
    SUM(liquidity_token_balance) AS total_liquidity
  FROM `bitcoin`.`liquidity_positions_largest`
  GROUP BY 1, 2
),

provider_rankings AS (
  SELECT
    user_id,
    pair_id,
    pair_token0_symbol || '-' || pair_token1_symbol AS pair_name,
    liquidity_token_balance,
    liquidity_token_balance / SUM(liquidity_token_balance) OVER (PARTITION BY pair_id) AS pool_share_pct,
    RANK() OVER (PARTITION BY pair_id ORDER BY liquidity_token_balance DESC) AS provider_rank
  FROM `bitcoin`.`liquidity_positions_largest`
)

SELECT
  p.user_id,
  p.pair_id,
  p.pair_name,
  p.liquidity_token_balance,
  p.pool_share_pct,
  p.provider_rank,
  s.total_liquidity,
  s.unique_providers
FROM provider_rankings p
JOIN pool_stats s ON p.pair_id = s.pair_id
WHERE p.provider_rank <= 10  -- Top 10 providers per pool
ORDER BY p.pair_id, p.provider_rank
  )