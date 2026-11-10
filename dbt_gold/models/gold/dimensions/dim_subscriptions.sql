{{ config(materialized='table') }}

SELECT
    subscription_id,
    account_id,
    plan,
    start_date,
    end_date,
    billing_cycle,
    status
FROM {{ ref('stg_subscriptions') }}