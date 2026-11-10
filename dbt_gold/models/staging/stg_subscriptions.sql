{{ config(materialized='view') }}

SELECT *
FROM read_parquet('../data/dev/silver/subscriptions/subscriptions.parquet')