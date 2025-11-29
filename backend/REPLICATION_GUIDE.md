# CouchDB Distributed Replication Setup Guide

## Overview

This guide will help you set up distributed replication for your NoteBook application using CouchDB. The system supports automatic failover, continuous synchronization, and cluster health monitoring.

## Features

- **Multi-Master Replication**: Bidirectional sync between all nodes
- **Automatic Failover**: Handle node failures gracefully  
- **Real-time Monitoring**: REST API endpoints for cluster health
- **Continuous Sync**: Real-time data synchronization
- **Load Balancing**: HAProxy integration for high availability
- **Health Checks**: Automated monitoring of all nodes

## Quick Start with Docker

### 1. Basic 3-Node Setup

```bash
# Clone and navigate to backend directory
cd backend/

# Start primary + 2 replica nodes
docker-compose up -d couchdb-primary couchdb-replica1 couchdb-replica2

# Start the backend with replication
docker-compose up -d notebook-backend
```

### 2. Full Cluster with Load Balancer

```bash
# Start full cluster including load balancer
docker-compose --profile loadbalancer --profile full-cluster up -d

# Access CouchDB through load balancer
# URL: http://localhost:5983/
# HAProxy Stats: http://localhost:8404/
```

## Manual Configuration

### 1. Environment Setup

Copy and configure the environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Primary CouchDB Server
COUCHDB_URL=http://localhost:5984/
COUCHDB_USER=Admin
COUCHDB_PASSWORD=password123

# Replication Nodes
REPLICATION_NODES=http://localhost:5985/,http://localhost:5986/

# Replication Settings  
CONTINUOUS_REPLICATION=true
REPLICATION_RETRY_SECONDS=30
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Application

```bash
python app.py
```

## Production Deployment

### 1. Cloud Configuration

For cloud deployment, update your environment variables:

```env
# Production Configuration
COUCHDB_URL=https://primary-couch.example.com:6984/
REPLICATION_NODES=https://replica1.example.com:6984/,https://replica2.example.com:6984/,https://replica3.example.com:6984/
COUCHDB_USER=your_admin_user
COUCHDB_PASSWORD=your_secure_password
CONTINUOUS_REPLICATION=true
```

### 2. Security Considerations

- Use HTTPS for all CouchDB connections
- Configure proper authentication and authorization
- Set up SSL certificates for CouchDB nodes
- Use secure passwords and consider certificate-based auth
- Configure firewall rules to restrict access

### 3. Monitoring Setup

The application provides several monitoring endpoints:

- **Health Check**: `GET /api/health`
- **Replication Status**: `GET /api/replication/status`
- **Cluster Health**: `GET /api/replication/health`
- **Replication Info**: `GET /api/replication/info`

## API Endpoints

### Replication Management

#### Get Replication Status
```bash
curl http://localhost:5000/api/replication/status
curl http://localhost:5000/api/replication/status?database=pdfs
```

#### Check Cluster Health  
```bash
curl http://localhost:5000/api/replication/health
```

#### Force Database Sync
```bash
curl -X POST http://localhost:5000/api/replication/sync \
  -H "Content-Type: application/json" \
  -d '{"database": "pdfs", "wait": true}'
```

#### Setup Replication for Database
```bash
curl -X POST http://localhost:5000/api/replication/setup \
  -H "Content-Type: application/json" \
  -d '{"database": "categories", "bidirectional": true}'
```

### Health Monitoring

#### Application Health
```bash
curl http://localhost:5000/api/health
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify CouchDB nodes are running
   - Check network connectivity between nodes
   - Confirm credentials are correct

2. **Replication Not Working**
   - Check replication status endpoint
   - Verify `_replicator` database exists
   - Review application logs for errors

3. **High CPU Usage**
   - Check for replication conflicts
   - Consider increasing `REPLICATION_RETRY_SECONDS`
   - Monitor database size and fragmentation

### Monitoring Commands

```bash
# Check CouchDB node status
curl http://admin:password@localhost:5984/_up

# View active replications
curl http://admin:password@localhost:5984/_replicator/_all_docs?include_docs=true

# Check database info
curl http://admin:password@localhost:5984/pdfs

# View replication logs
docker-compose logs -f notebook-backend
```

## Performance Optimization

### 1. Database Design

- Use appropriate document sizes (< 1MB recommended)
- Design efficient indexes
- Consider document partitioning for large datasets
- Use bulk operations when possible

### 2. Replication Tuning

- Adjust `REPLICATION_RETRY_SECONDS` based on network latency
- Use filtered replication for selective sync
- Consider batch sizes for large replications
- Monitor memory usage during sync

### 3. Network Optimization

- Use compression for network transfers
- Configure appropriate timeouts
- Consider network topology (avoid cross-region replication if possible)
- Use dedicated network for cluster communication

## Backup Strategy

### 1. Automated Backups

```bash
# Backup specific database
curl -X GET http://admin:password@localhost:5984/pdfs/_all_docs?include_docs=true > pdfs_backup.json

# Scheduled backup script (add to crontab)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
curl -X GET http://admin:password@localhost:5984/pdfs/_all_docs?include_docs=true > backup_${DATE}.json
```

### 2. Disaster Recovery

1. **Node Failure Recovery**:
   - Failed nodes automatically excluded from replication
   - Data remains available on healthy nodes
   - Replace failed node and restart replication

2. **Complete Cluster Recovery**:
   - Restore from backup to new cluster
   - Reconfigure replication nodes
   - Verify data integrity

## Scaling

### Adding New Nodes

1. Start new CouchDB instance
2. Add to `REPLICATION_NODES` environment variable
3. Restart application
4. Replication automatically configures for existing databases

### Load Balancing

Use HAProxy or similar for distributing read requests:

```bash
# Start with load balancer
docker-compose --profile loadbalancer up -d
```

## Security Best Practices

1. **Authentication**
   - Use strong passwords
   - Consider certificate-based authentication
   - Regularly rotate credentials

2. **Network Security**
   - Use HTTPS/SSL for all connections
   - Configure firewall rules
   - Isolate cluster network

3. **Database Security**
   - Enable CouchDB authentication
   - Configure database-level permissions
   - Regular security audits

## Support

For issues and questions:
- Check application logs: `docker-compose logs notebook-backend`
- Review CouchDB documentation: https://docs.couchdb.org/
- Monitor cluster health via API endpoints