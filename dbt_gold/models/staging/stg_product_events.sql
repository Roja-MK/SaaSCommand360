{{ config(materialized='view') }}

SELECT *
FROM read_parquet('../data/dev/silver/product_events/product_events.parquet')