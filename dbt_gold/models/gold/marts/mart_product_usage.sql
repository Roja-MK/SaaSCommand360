{{ config(materialized='table') }}

SELECT
    feature,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    MIN(event_timestamp) AS first_event,
    MAX(event_timestamp) AS last_event

FROM {{ ref('fact_product_events') }}

GROUP BY feature
ORDER BY total_events DESC