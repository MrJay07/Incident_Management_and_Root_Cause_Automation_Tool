CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    service VARCHAR(128) NOT NULL,
    level VARCHAR(32) NOT NULL,
    message TEXT NOT NULL,
    raw_line TEXT NOT NULL
);

CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    service VARCHAR(128) NOT NULL,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    source_log_id INTEGER REFERENCES logs(id)
);

CREATE TABLE rca_reports (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    summary TEXT NOT NULL,
    timeline JSONB NOT NULL,
    bottleneck VARCHAR(255) NOT NULL,
    dependencies JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    channel VARCHAR(64) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    error_message TEXT
);
