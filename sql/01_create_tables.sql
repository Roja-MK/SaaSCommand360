CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry VARCHAR(100),
    size VARCHAR(50),
    region VARCHAR(100),
    owner VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    role VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    plan VARCHAR(50),
    start_date DATE,
    end_date DATE,
    billing_cycle VARCHAR(30),
    status VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    subscription_id VARCHAR(20) NOT NULL REFERENCES subscriptions(subscription_id),
    amount NUMERIC(12,2),
    invoice_date DATE,
    due_date DATE,
    paid_date DATE,
    status VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    severity VARCHAR(30),
    status VARCHAR(30),
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_events (
    event_id VARCHAR(30) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL REFERENCES users(user_id),
    feature VARCHAR(100),
    event_timestamp TIMESTAMP
);
