USE aml_analysis;

-- Run these statements once after the full import.
CREATE INDEX idx_transactions_time
    ON transactions (transaction_time);

CREATE INDEX idx_sender_time
    ON transactions (from_bank, from_account, transaction_time);

CREATE INDEX idx_currency_amount
    ON transactions (payment_currency, amount_paid DESC);

-- Main analysis period: dates with normal transaction volume.
CREATE TABLE daily_account_stats AS
SELECT
    DATE(transaction_time) AS transaction_date,
    from_bank,
    from_account,
    COUNT(*) AS daily_transaction_count,
    SUM(is_laundering) AS daily_laundering_count
FROM transactions
WHERE transaction_time < '2022-09-11'
GROUP BY
    DATE(transaction_time),
    from_bank,
    from_account;

CREATE INDEX idx_daily_frequency
    ON daily_account_stats (transaction_date, daily_transaction_count DESC);
