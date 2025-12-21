-- Migration: Create context_snapshot table for Redis fallback
-- Date: 2025-12-17
-- Purpose: Permanent storage for context data with Redis → DB fallback

CREATE TABLE IF NOT EXISTS context_snapshots (
    -- Primary Key
    context_id VARCHAR(64) PRIMARY KEY,
    
    -- Context Data
    context_data TEXT NOT NULL,
    context_type VARCHAR(50) NOT NULL,
    
    -- Metadata
    parcel_id VARCHAR(100),
    frozen BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    accessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER NOT NULL DEFAULT 0,
    
    -- Source Tracking
    created_by VARCHAR(50) DEFAULT 'system',
    redis_ttl_seconds INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_context_snapshots_parcel_id ON context_snapshots(parcel_id);
CREATE INDEX IF NOT EXISTS idx_context_snapshots_created_at ON context_snapshots(created_at);
CREATE INDEX IF NOT EXISTS idx_context_snapshots_context_type ON context_snapshots(context_type);

-- Comments (PostgreSQL)
COMMENT ON TABLE context_snapshots IS 'Permanent backup for Redis context storage with automatic fallback';
COMMENT ON COLUMN context_snapshots.context_id IS 'Unique context identifier (matches Redis key)';
COMMENT ON COLUMN context_snapshots.context_data IS 'Serialized JSON context data';
COMMENT ON COLUMN context_snapshots.expires_at IS 'NULL = never expires';
COMMENT ON COLUMN context_snapshots.access_count IS 'Track fallback usage frequency';
