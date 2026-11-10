{{ config(materialized='table') }}

SELECT
    user_id,
    account_id,
    role,
    created_at
FROM {{ ref('stg_users') }}