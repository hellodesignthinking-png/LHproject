# Database Migration Guide

## Overview

This directory contains database migration scripts for ZeroSite v11.0 production deployment.

## Quick Start

### 1. Run Migration

```bash
# Using default SQLite database
python3 scripts/migrate_db.py

# Using custom database URL
DATABASE_URL="postgresql://user:pass@localhost/zerosite" python3 scripts/migrate_db.py
```

### 2. Verify Migration

The script automatically verifies the migration. Look for:
```
✅ Migration and verification completed successfully!
```

## Tables Created

### context_snapshots
Permanent storage for pipeline analysis contexts with Redis fallback support.

**Columns:**
- `context_id` (VARCHAR(64), PRIMARY KEY) - Unique context identifier
- `context_data` (TEXT) - JSON-serialized context data
- `context_type` (VARCHAR(50)) - Context type (e.g., 'M1_FINAL')
- `parcel_id` (VARCHAR(100), INDEX) - Related parcel ID
- `frozen` (BOOLEAN) - Whether context is frozen/immutable
- `created_at` (DATETIME) - Creation timestamp
- `expires_at` (DATETIME, NULLABLE) - Expiration timestamp
- `accessed_at` (DATETIME, NULLABLE) - Last access timestamp
- `access_count` (INTEGER) - Number of times accessed
- `created_by` (VARCHAR(50)) - Creator identifier
- `redis_ttl_seconds` (INTEGER, NULLABLE) - Original Redis TTL

**Indices:**
- PRIMARY KEY on `context_id`
- INDEX on `parcel_id`
- INDEX on `context_id` (for faster lookups)

## Environment Variables

### DATABASE_URL
Database connection string. Defaults to `sqlite:///zerosite.db`

**Examples:**
```bash
# SQLite (default)
DATABASE_URL="sqlite:///zerosite.db"

# PostgreSQL
DATABASE_URL="postgresql://user:password@localhost:5432/zerosite"

# MySQL
DATABASE_URL="mysql+pymysql://user:password@localhost:3306/zerosite"
```

## Production Deployment

### 1. Pre-deployment Checklist

- [ ] Backup existing database
- [ ] Set correct `DATABASE_URL` environment variable
- [ ] Ensure database server is accessible
- [ ] Check disk space for database growth

### 2. Migration Steps

```bash
# 1. Backup existing database (if any)
cp zerosite.db zerosite.db.backup

# 2. Run migration
python3 scripts/migrate_db.py

# 3. Check migration log for errors
# (Script will exit with code 0 on success, non-zero on failure)

# 4. Verify tables were created
sqlite3 zerosite.db ".tables"
```

### 3. Post-migration

- Restart application services
- Monitor application logs for database errors
- Test context storage/retrieval functionality

## Rollback

If migration fails, restore from backup:

```bash
# SQLite
cp zerosite.db.backup zerosite.db

# PostgreSQL
pg_restore -d zerosite backup.dump

# MySQL
mysql zerosite < backup.sql
```

## Troubleshooting

### Error: "Table already exists"
This is normal - the script uses `CREATE TABLE IF NOT EXISTS` and will skip existing tables.

### Error: "Permission denied"
Ensure the application user has write permissions to the database directory (for SQLite) or database server (for PostgreSQL/MySQL).

### Error: "Module not found"
Ensure you're running the script from the project root directory:
```bash
cd /path/to/webapp
python3 scripts/migrate_db.py
```

## Database Schema Version

**Current Version**: 1.0  
**Date**: 2025-12-27  
**Changes**: Initial schema with context_snapshots table

## Future Migrations

Future schema changes will be tracked here:

- [ ] v1.1: Add context_history table (planned)
- [ ] v1.2: Add user_preferences table (planned)
- [ ] v1.3: Add audit_log table (planned)

## Support

For issues or questions:
- Check logs in `/tmp/backend_*.log`
- Review migration output
- Contact: ZeroSite Dev Team

---

**Last Updated**: 2025-12-27  
**Maintained by**: ZeroSite Development Team
