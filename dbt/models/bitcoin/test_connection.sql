-- models/test_connection.sql
{{
  config(
    materialized='view',
    schema='default'
  )
}}

SELECT 'swaps_latest' AS table_name, 
       count() AS row_count 
FROM bitcoin.swaps_latest