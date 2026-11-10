{{ config(materialized='table') }}

SELECT
    event_id,
    user_id,
    feature,
    event_timestamp

FROM {{ ref('stg_product_events') }}