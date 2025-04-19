
  
    
    
    
        
        insert into `bitcoin_bitcoin_derived`.`pairs_recently_created__dbt_backup`
        ("pair_id", "created_at_timestamp", "created_at_block_number", "token0_symbol", "token0_id", "token1_symbol", "token1_id", "total_liquidity_usd", "total_liquidity_eth", "pair_symbol")

SELECT
    id as pair_id,
    parseDateTimeBestEffort(created_at_timestamp) as created_at_timestamp,
    created_at_block_number,
    token0_symbol,
    token0_id,
    token1_symbol,
    token1_id,
    reserve_u_s_d as total_liquidity_usd,
    reserve_e_t_h as total_liquidity_eth,
    concat(token0_symbol, '-', token1_symbol) as pair_symbol
FROM `bitcoin`.`pairs_recently_created`
  
  