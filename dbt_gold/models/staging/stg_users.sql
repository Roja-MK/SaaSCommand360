{{ config(materialized='view') }}

SELECT *
FROM read_parquet('../data/dev/silver/users/users.parquet')