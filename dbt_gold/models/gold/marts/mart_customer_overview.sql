{{ config(materialized='table') }}

SELECT
    a.account_id,
    a.company_name,
    a.industry,
    a.size,
    a.region,

    COUNT(DISTINCT u.user_id) AS total_users,

    COUNT(DISTINCT s.subscription_id) AS total_subscriptions,

    COUNT(DISTINCT CASE
        WHEN s.status = 'Active'
        THEN s.subscription_id
    END) AS active_subscriptions,

    COUNT(DISTINCT CASE
        WHEN s.status = 'Cancelled'
        THEN s.subscription_id
    END) AS cancelled_subscriptions

FROM {{ ref('dim_accounts') }} a

LEFT JOIN {{ ref('dim_users') }} u
    ON a.account_id = u.account_id

LEFT JOIN {{ ref('dim_subscriptions') }} s
    ON a.account_id = s.account_id

GROUP BY
    a.account_id,
    a.company_name,
    a.industry,
    a.size,
    a.region