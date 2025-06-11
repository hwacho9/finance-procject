-- Initialize macro_finance database
-- This script runs when the PostgreSQL container starts

-- Create database if not exists (handled by POSTGRES_DB env var)

-- Create basic extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial schemas (tables will be created by SQLAlchemy)
-- This is just a placeholder for any custom initialization

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE macro_finance TO postgres;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Macro Finance database initialized successfully';
END $$; 