

WITH pair_metrics AS (
  SELECT
    id AS pair_address,
    token0_symbol || '-' || token1_symbol AS pair_name,
    parseDateTimeBestEffort(created_at_timestamp) AS creation_time,
    created_at_block_number,
    token0_id,
    token1_id,
    reserve_u_s_d,
    reserve_e_t_h,
    reserve_u_s_d / NULLIF(reserve_e_t_h, 0) AS usd_per_eth_price,
    -- Calculate hourly age of the pair
    dateDiff('hour', creation_time, now()) AS hours_since_creation
  FROM `bitcoin`.`pairs_recently_created`
)

SELECT
  pair_address,
  pair_name,
  creation_time,
  hours_since_creation,
  reserve_u_s_d AS total_liquidity_usd,
  reserve_e_t_h AS total_liquidity_eth,
  usd_per_eth_price,
  CASE
    WHEN reserve_u_s_d > 1000000 THEN 'Large'
    WHEN reserve_u_s_d > 100000 THEN 'Medium'
    ELSE 'Small'
  END AS liquidity_size,
  -- Normalize by pair age
  reserve_u_s_d / NULLIF(hours_since_creation, 0) AS hourly_liquidity_growth_usd
FROM pair_metrics
ORDER BY creation_time DESC