

  create view `bitcoin_bitcoin_derived`.`swaps_latest_for_pair` 
  
    
    
  as (
    

SELECT
    id as swap_id,
    transaction_id,
    parseDateTimeBestEffort(transaction_timestamp) as transaction_timestamp,
    pair_token0_symbol,
    pair_token1_symbol,
    amount0_in,
    amount1_in,
    amount0_out,
    amount1_out,
    amount_u_s_d as amount_usd,
    -- Calculate derived metrics
    concat(pair_token0_symbol, '-', pair_token1_symbol) as pair_symbol,
    CASE 
        WHEN amount0_in > 0 THEN pair_token0_symbol
        WHEN amount1_in > 0 THEN pair_token1_symbol
        ELSE NULL
    END as token_in_symbol,
    CASE 
        WHEN amount0_out > 0 THEN pair_token0_symbol
        WHEN amount1_out > 0 THEN pair_token1_symbol
        ELSE NULL
    END as token_out_symbol,
    -- Calculate absolute amounts
    greatest(amount0_in, amount1_in) as amount_in,
    greatest(amount0_out, amount1_out) as amount_out,
    -- Calculate swap direction
    CASE
        WHEN amount0_in > 0 AND amount1_out > 0 THEN 'token0_to_token1'
        WHEN amount1_in > 0 AND amount0_out > 0 THEN 'token1_to_token0'
        ELSE 'complex'
    END as swap_direction
FROM `bitcoin`.`swaps_latest_for_pair`
  )