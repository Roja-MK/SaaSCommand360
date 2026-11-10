{{ config(materialized='table') }}

SELECT
    account_id,
    company_name,
    industry,
    size,
    region,
    owner
FROM {{ ref('stg_accounts') }}