-- models/test_connection.sql


SELECT 'swaps_latest' AS table_name, 
       count() AS row_count 
FROM bitcoin.swaps_latest