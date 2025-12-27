# Redis Setup Guide

## Overview

ZeroSite v11.0 uses Redis for high-performance context caching with automatic fallback to in-memory storage.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Context Storage Strategy                       │
│                                                 │
│  1. Redis (Primary)    → Fast, persistent       │
│  2. In-Memory (Fallback) → Fast, temporary      │
│  3. Database (Backup)  → Slow, permanent        │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Disable Redis (Use In-Memory)

No setup required! The system works perfectly with in-memory storage.

```bash
# In .env file:
REDIS_ENABLED=false
```

### Option 2: Enable Redis (Recommended for Production)

#### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name zerosite-redis redis:7-alpine
```

#### 2. Configure Environment

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=          # Leave empty if no password
REDIS_SSL=false
```

#### 3. Test Connection

```bash
python3 app/config/redis_config.py
```

Expected output:
```
✅ Redis is available!
   Server Info: 7.x.x
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_ENABLED` | `true` | Enable/disable Redis |
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number (0-15) |
| `REDIS_PASSWORD` | `None` | Redis password (if required) |
| `REDIS_SSL` | `false` | Enable SSL/TLS connection |

### Redis Server Configuration

Edit `/etc/redis/redis.conf` (Ubuntu/Debian):

```conf
# Bind to all interfaces (for remote access)
bind 0.0.0.0

# Set password
requirepass your_strong_password_here

# Enable persistence
save 900 1
save 300 10
save 60 10000

# Max memory policy
maxmemory 256mb
maxmemory-policy allkeys-lru
```

Restart Redis:
```bash
sudo systemctl restart redis-server
```

## Production Deployment

### 1. Security Best Practices

#### Set Password
```bash
# In redis.conf:
requirepass YOUR_STRONG_PASSWORD

# In .env:
REDIS_PASSWORD=YOUR_STRONG_PASSWORD
```

#### Enable SSL/TLS
```bash
# In redis.conf:
tls-port 6380
port 0  # Disable non-TLS
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt

# In .env:
REDIS_PORT=6380
REDIS_SSL=true
```

#### Firewall Rules
```bash
# Allow only application server
sudo ufw allow from <app_server_ip> to any port 6379
```

### 2. Performance Tuning

#### Redis Configuration
```conf
# Increase max connections
maxclients 10000

# Optimize memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Enable RDB snapshots
save 900 1
save 300 10
save 60 10000

# Enable AOF for durability
appendonly yes
appendfsync everysec
```

#### Monitoring
```bash
# Check Redis stats
redis-cli INFO stats

# Monitor commands in real-time
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory
```

### 3. High Availability (Optional)

#### Redis Sentinel (Master-Slave)
```bash
# Setup master-slave replication
# Master: redis.conf
bind 0.0.0.0
requirepass master_password

# Slave: redis.conf
bind 0.0.0.0
requirepass slave_password
replicaof <master_ip> 6379
masterauth master_password
```

#### Redis Cluster (Sharding)
For very high loads, consider Redis Cluster with multiple nodes.

## Troubleshooting

### Connection Refused
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Check port
sudo netstat -tlnp | grep 6379

# Test connection
redis-cli ping
```

### Permission Denied
```bash
# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Fix permissions
sudo chown redis:redis /var/lib/redis
```

### Out of Memory
```bash
# Check memory usage
redis-cli INFO memory

# Flush all keys (CAUTION: destructive!)
redis-cli FLUSHALL

# Or set max memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Slow Performance
```bash
# Check slow queries
redis-cli SLOWLOG GET 10

# Monitor latency
redis-cli --latency

# Check connected clients
redis-cli CLIENT LIST
```

## Testing

### Manual Test
```bash
# Set a key
redis-cli SET test "hello"

# Get the key
redis-cli GET test

# Check TTL
redis-cli TTL test

# Delete the key
redis-cli DEL test
```

### Application Test
```python
from app.config.redis_config import get_redis_client

client = get_redis_client()
if client:
    client.set('test_key', 'test_value', ex=60)
    value = client.get('test_key')
    print(f"Value: {value}")
else:
    print("Redis not available, using in-memory fallback")
```

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Memory Usage** - Should stay under maxmemory
2. **Hit Rate** - keyspace_hits / (keyspace_hits + keyspace_misses)
3. **Connected Clients** - Should be stable
4. **Evicted Keys** - Should be low
5. **Blocked Clients** - Should be 0

### Grafana Dashboard (Optional)
- Use Redis Exporter for Prometheus
- Import Redis dashboard template
- Set up alerts for critical metrics

## Backup & Recovery

### Backup
```bash
# RDB snapshot
redis-cli SAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backup/dump-$(date +%Y%m%d).rdb

# AOF backup
cp /var/lib/redis/appendonly.aof /backup/
```

### Recovery
```bash
# Stop Redis
sudo systemctl stop redis-server

# Restore RDB
cp /backup/dump.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis-server
```

## FAQ

**Q: Do I need Redis for the system to work?**  
A: No! The system works perfectly with in-memory storage. Redis is optional for better performance in production.

**Q: What happens if Redis goes down?**  
A: The system automatically falls back to in-memory storage. No data loss for active sessions.

**Q: How much memory does Redis need?**  
A: Start with 256MB-1GB. Monitor and adjust based on usage.

**Q: Can I use Redis Cloud/ElastiCache?**  
A: Yes! Just set `REDIS_HOST` to your cloud Redis endpoint.

---

**Last Updated**: 2025-12-27  
**Version**: 1.0  
**Maintained by**: ZeroSite Development Team
