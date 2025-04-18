import clickhouse_connect

def load_to_clickhouse():
    client = clickhouse_connect.get_client(
        host='bitcoin-etl-pipeline-clickhouse-1',
        port=8123,
        username='admin',
        password='password',
        database='bitcoin'
    )


    def create_and_load_table(table_name, s3_url, schema, order_by='id'):
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {schema}
        )
        ENGINE = MergeTree
        ORDER BY {order_by}
        """
        client.command(create_sql)
        print(f"✅ Table '{table_name}' created or already exists.")

        insert_sql = f"""
        INSERT INTO {table_name}
        SELECT *
        FROM s3(
            '{s3_url}',
            'JSONEachRow',
            '{schema}'
        )
        """
        client.command(insert_sql)
        print(f"✅ NDJSON data from '{s3_url}' loaded into '{table_name}'.")


    create_and_load_table(
        "liquidity_positions_largest",
        "https://swap-etl-wbtc.s3.amazonaws.com/liquidity_positions_largest.ndjson",
        """
            liquidity_token_balance Float64,
            id String,
            pair_token0_symbol String,
            pair_token1_symbol String,
            pair_id String,
            user_id String
        """
    )

    create_and_load_table(
        "pairs_recently_created",
        "https://swap-etl-wbtc.s3.amazonaws.com/pairs_recently_created.ndjson",
        """
            id String,
            created_at_timestamp String,
            created_at_block_number UInt32,
            token0_symbol String,
            token0_id String,
            token1_symbol String,
            token1_id String,
            reserve_u_s_d Float64,
            reserve_e_t_h Float64
        """,
        order_by="created_at_timestamp"
    )

    create_and_load_table(
        "swaps_latest_for_pair",
        "https://swap-etl-wbtc.s3.amazonaws.com/swaps_latest_for_pair.ndjson",
        """
            id String,
            transaction_id String,
            transaction_timestamp String,
            pair_token0_symbol String,
            pair_token1_symbol String,
            amount0_in Float64,
            amount1_in Float64,
            amount0_out Float64,
            amount1_out Float64,
            amount_u_s_d Float64
        """,
        order_by="transaction_timestamp"
    )

    create_and_load_table(
        "swaps_latest_large",
        "https://swap-etl-wbtc.s3.amazonaws.com/swaps_latest_large.ndjson",
        """
            id String,
            transaction_id String,
            transaction_timestamp String,
            pair_token0_symbol String,
            pair_token1_symbol String,
            amount0_in Float64,
            amount1_in Float64,
            amount0_out Float64,
            amount1_out Float64,
            amount_u_s_d Float64
        """,
        order_by="transaction_timestamp"
    )

    create_and_load_table(
        "swaps_latest",
        "https://swap-etl-wbtc.s3.amazonaws.com/swaps_latest.ndjson",
        """
            id String,
            transaction_id String,
            transaction_timestamp String,
            pair_token0_symbol String,
            pair_token1_symbol String,
            amount0_in Float64,
            amount1_in Float64,
            amount0_out Float64,
            amount1_out Float64,
            amount_u_s_d Float64
        """,
        order_by="transaction_timestamp"
    )

    create_and_load_table(
        "token_price",
        "https://swap-etl-wbtc.s3.amazonaws.com/token_price.ndjson",
        """
            id String,
            symbol String,
            name String,
            derivedETH Float64
        """,
        order_by="id"
    )

    create_and_load_table(
    "trading_volume_daily_for_pair",
    "https://swap-etl-wbtc.s3.amazonaws.com/trading_volume_daily_for_pair.ndjson",
    """
        date DateTime,
        daily_volume_u_s_d Float64,
        daily_txns Float64,
        daily_volume_token0 Float64,
        daily_volume_token1 Float64
    """,
    order_by="date"
)


    create_and_load_table(
        "trading_volume_hourly_for_pair",
        "https://swap-etl-wbtc.s3.amazonaws.com/trading_volume_hourly_for_pair.ndjson",
        """
            hour_start_unix String,
            hourly_volume_token0 Float64,
            hourly_volume_token1 Float64,
            hourly_volume_u_s_d Float64,
            hourly_txns Float64
        """,
        order_by="hour_start_unix"
    )

    create_and_load_table(
    "uniswap_daily_data",
    "https://swap-etl-wbtc.s3.amazonaws.com/uniswap_daily_data.ndjson",
    """
        date String,
        daily_volume_e_t_h Float64,
        daily_volume_u_s_d Float64,
        total_liquidity_e_t_h Float64,
        total_liquidity_u_s_d Float64
    """,
    order_by="date"
    )
    create_and_load_table(
        "erc20_transfers_wbtc",
        "https://swap-etl-wbtc.s3.amazonaws.com/erc20_transfers_wbtc.ndjson",
        """
            block_number UInt32,
            transaction_index UInt32,
            log_index UInt32,
            transaction_hash String,
            erc20 String,
            from_address String,
            to_address String,
            value_binary String,
            value_string String,
            value_f64 Float64,
            chain_id UInt8,
            wbtc_amount Float64
        """,
        order_by="block_number"
    )

    print("\n🎉 All tables created and NDJSON data loaded successfully.")
