CREATE DATABASE IF NOT EXISTS aml_analysis
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE aml_analysis;

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_time DATETIME,
    from_bank VARCHAR(20),
    from_account VARCHAR(40),
    to_bank VARCHAR(20),
    to_account VARCHAR(40),
    amount_received DECIMAL(20, 2),
    receiving_currency VARCHAR(30),
    amount_paid DECIMAL(20, 2),
    payment_currency VARCHAR(30),
    payment_format VARCHAR(30),
    is_laundering BOOLEAN
);

DESCRIBE transactions;
