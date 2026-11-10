{{ config(materialized='table') }}

SELECT
    ticket_id,
    account_id,
    severity,
    status,
    created_at,
    resolved_at
FROM {{ ref('stg_support_tickets') }}