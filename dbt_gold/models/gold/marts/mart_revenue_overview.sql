{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('month', invoice_date)::DATE AS invoice_month,
    COUNT(*) AS total_invoices,
    ROUND(SUM(amount), 2) AS total_billed_amount,

    SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END)
        AS paid_invoice_count,

    ROUND(
        SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 2
    ) AS paid_revenue,

    SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END)
        AS overdue_invoice_count,

    ROUND(
        SUM(CASE WHEN status = 'Overdue' THEN amount ELSE 0 END), 2
    ) AS overdue_amount,

    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END)
        AS pending_invoice_count,

    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END)
        AS failed_invoice_count

FROM {{ ref('fact_invoices') }}

GROUP BY 1
ORDER BY 1