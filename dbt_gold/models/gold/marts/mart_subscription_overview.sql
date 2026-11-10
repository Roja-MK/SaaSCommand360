{{ config(materialized='table') }}

SELECT
    plan,

    COUNT(*) AS total_subscriptions,

    COUNT(DISTINCT account_id) AS total_accounts,

    SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END)
        AS active_subscriptions,

    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)
        AS cancelled_subscriptions,

    SUM(CASE WHEN status = 'Past Due' THEN 1 ELSE 0 END)
        AS past_due_subscriptions

FROM {{ ref('dim_subscriptions') }}

GROUP BY plan
ORDER BY total_subscriptions DESC