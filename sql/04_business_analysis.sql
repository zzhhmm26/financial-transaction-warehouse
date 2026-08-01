USE aml_analysis;

-- 1. Currency-level transaction counts and amounts.
-- Amounts are not compared across currencies without exchange-rate conversion.
SELECT
    payment_currency,
    COUNT(*) AS transaction_count,
    SUM(amount_paid) AS total_amount,
    ROUND(AVG(amount_paid), 2) AS average_amount,
    MAX(amount_paid) AS maximum_amount,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM transactions) * 100, 2)
        AS transaction_share_pct
FROM transactions
GROUP BY payment_currency
ORDER BY transaction_count DESC;

-- 2. Large transactions in the 1,000,000-row development sample:
-- top 1% by amount within each payment currency.
WITH amount_rank AS (
    SELECT
        transaction_id,
        payment_currency,
        amount_paid,
        is_laundering,
        NTILE(100) OVER (
            PARTITION BY payment_currency
            ORDER BY amount_paid DESC
        ) AS amount_group
    FROM transactions
    WHERE transaction_id <= 1000000
)
SELECT
    CASE
        WHEN amount_group = 1 THEN 'large'
        ELSE 'other'
    END AS amount_type,
    COUNT(*) AS transaction_count,
    SUM(is_laundering) AS laundering_count,
    ROUND(AVG(is_laundering) * 100, 4) AS laundering_rate_pct
FROM amount_rank
GROUP BY amount_type
ORDER BY amount_type;

-- 3. High-frequency account-days in the main analysis period.
WITH daily_rank AS (
    SELECT
        *,
        NTILE(100) OVER (
            PARTITION BY transaction_date
            ORDER BY daily_transaction_count DESC
        ) AS frequency_group
    FROM daily_account_stats
)
SELECT
    CASE
        WHEN frequency_group = 1 THEN 'high_frequency'
        ELSE 'other'
    END AS frequency_type,
    COUNT(*) AS account_day_count,
    SUM(daily_transaction_count) AS transaction_count,
    SUM(daily_laundering_count) AS laundering_count,
    ROUND(
        SUM(daily_laundering_count) / SUM(daily_transaction_count) * 100,
        4
    ) AS laundering_rate_pct
FROM daily_rank
GROUP BY frequency_type
ORDER BY frequency_type;

-- 4. Sensitivity analysis including the sparse tail after 2022-09-10.
WITH tail_stats AS (
    SELECT
        DATE(transaction_time) AS transaction_date,
        from_bank,
        from_account,
        COUNT(*) AS daily_transaction_count,
        SUM(is_laundering) AS daily_laundering_count
    FROM transactions
    WHERE transaction_time >= '2022-09-11'
    GROUP BY
        DATE(transaction_time),
        from_bank,
        from_account
),
all_daily_stats AS (
    SELECT * FROM daily_account_stats
    UNION ALL
    SELECT * FROM tail_stats
),
daily_rank AS (
    SELECT
        *,
        NTILE(100) OVER (
            PARTITION BY transaction_date
            ORDER BY daily_transaction_count DESC
        ) AS frequency_group
    FROM all_daily_stats
)
SELECT
    CASE
        WHEN frequency_group = 1 THEN 'high_frequency'
        ELSE 'other'
    END AS frequency_type,
    COUNT(*) AS account_day_count,
    SUM(daily_transaction_count) AS transaction_count,
    SUM(daily_laundering_count) AS laundering_count,
    ROUND(
        SUM(daily_laundering_count) / SUM(daily_transaction_count) * 100,
        4
    ) AS laundering_rate_pct
FROM daily_rank
GROUP BY frequency_type
ORDER BY frequency_type;
