{{ config(materialized='table') }}

SELECT
    invoice_id,
    account_id,
    subscription_id,
    amount,
    invoice_date,
    due_date,
    paid_date,
    status
FROM {{ ref('stg_invoices') }}