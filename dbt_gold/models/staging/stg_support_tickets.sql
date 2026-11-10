{{ config(materialized='view') }}

SELECT *
FROM read_parquet('../data/dev/silver/support_tickets/support_tickets.parquet')