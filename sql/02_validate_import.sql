USE aml_analysis;

SELECT
    COUNT(*) AS transaction_count,
    SUM(is_laundering) AS laundering_count,
    MIN(transaction_time) AS earliest_time,
    MAX(transaction_time) AS latest_time
FROM transactions;

SELECT
    is_laundering,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY is_laundering
ORDER BY is_laundering;
