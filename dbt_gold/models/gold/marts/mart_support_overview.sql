{{ config(materialized='table') }}

SELECT
    severity,
    COUNT(*) AS total_tickets,

    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END)
        AS open_tickets,

    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END)
        AS in_progress_tickets,

    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END)
        AS resolved_tickets,

    ROUND(
        AVG(
            CASE
                WHEN resolved_at IS NOT NULL
                THEN DATE_DIFF('hour', created_at, resolved_at)
            END
        ), 2
    ) AS avg_resolution_hours

FROM {{ ref('fact_support_tickets') }}

GROUP BY severity
ORDER BY total_tickets DESC