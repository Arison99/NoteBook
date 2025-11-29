# NoteBook Backend Architecture

## 📁 Project Structure

```
backend/
├── src/                              # Source code
│   └── notebook/                     # Main package
│       ├── __init__.py              # Package metadata
│       ├── api/                     # API layer (GraphQL, REST)
│       │   ├── __init__.py
│       │   └── app.py               # Flask application factory
│       ├── core/                    # Core business logic
│       │   ├── __init__.py
│       │   ├── domain.py            # Domain models
│       │   └── schema.py            # GraphQL schema
│       ├── database/                # Data layer
│       │   ├── __init__.py
│       │   ├── couchdb_client.py    # CouchDB client & replication
│       │   ├── repository.py        # Data repositories
│       │   └── activity_repository.py # Activity tracking
│       ├── services/                # Business services
│       │   ├── __init__.py
│       │   ├── service.py           # Core services
│       │   └── analytics_service.py # Analytics services
│       └── utils/                   # Utilities
│           ├── __init__.py
│           └── crypto_utils.py      # Cryptographic utilities
├── config/                          # Configuration
│   ├── __init__.py                  # Config package
│   ├── settings.py                  # Application settings
│   ├── encryption.key               # Encryption key
│   └── key_store.json              # Key storage
├── scripts/                         # Utility scripts
│   └── monitor_cluster.py           # Cluster monitoring
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_couchdb_client.py
│   │   ├── test_app.py
│   │   └── test_monitor_cluster.py
│   └── integration/                # Integration tests
│       ├── __init__.py
│       └── test_deployment.py
├── docs/                           # Documentation
│   ├── testing.md                  # Testing guide
│   └── architecture.md             # This file
├── main.py                         # Application entry point
├── setup.py                        # Package setup
├── MANIFEST.in                     # Package manifest
├── requirements.txt                # Dependencies
├── pytest.ini                     # Test configuration
├── run_tests.py                   # Test runner
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-container setup
└── haproxy.cfg                    # Load balancer config
```

## 🏗️ Architecture Overview

### **Layered Architecture**

The application follows a clean, layered architecture pattern:

1. **API Layer** (`src/notebook/api/`)
   - Flask application with factory pattern
   - GraphQL endpoint via Ariadne
   - REST API for replication management
   - CORS configuration and middleware

2. **Core Layer** (`src/notebook/core/`)
   - Domain models and business entities
   - GraphQL schema definitions
   - Business rules and validations

3. **Data Layer** (`src/notebook/database/`)
   - CouchDB client with replication support
   - Repository pattern for data access
   - Activity tracking and logging

4. **Service Layer** (`src/notebook/services/`)
   - Business logic and orchestration
   - Analytics and reporting services
   - Cross-cutting concerns

5. **Utility Layer** (`src/notebook/utils/`)
   - Cryptographic functions
   - Helper utilities
   - Common functionality

### **Configuration Management**

Centralized configuration system with environment-specific settings:

- **Development**: Debug mode, local database
- **Production**: Security hardened, distributed setup
- **Testing**: Isolated test environment

### **Dependency Injection**

The application uses Flask's application factory pattern for:
- Configuration injection
- Service initialization
- Route registration
- Middleware setup

## 🚀 Running the Application

### **Development Mode**

```bash
# Install in development mode
pip install -e .

# Run the application
python main.py

# Or using the console script
notebook-server
```

### **Production Mode**

```bash
# Set environment
export FLASK_ENV=production
export SECRET_KEY=your-secret-key

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "notebook.api.app:create_app()"
```

### **Using Docker**

```bash
# Single container
docker build -t notebook-backend .
docker run -p 5000:5000 notebook-backend

# Full distributed setup
docker-compose up -d
```

## 🧪 Testing Architecture

### **Test Structure**

- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Cross-component and system tests
- **Fixtures**: Reusable test components in `conftest.py`

### **Running Tests**

```bash
# All tests
python run_tests.py

# Specific categories
python run_tests.py --unit
python run_tests.py --integration

# With coverage
python run_tests.py --coverage
```

## 📦 Package Management

### **Installation**

```bash
# Development installation
pip install -e .

# Production installation
pip install .

# Install with test dependencies
pip install -e ".[test]"
```

### **Building Distribution**

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Upload to PyPI (if public)
twine upload dist/*
```

## 🔧 Configuration Guide

### **Environment Variables**

```env
# Application
FLASK_ENV=development|production|testing
SECRET_KEY=your-secret-key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database
COUCHDB_URL=http://localhost:5984/
COUCHDB_USER=admin
COUCHDB_PASSWORD=password

# Replication
REPLICATION_NODES=http://replica1:5984/,http://replica2:5984/
CONTINUOUS_REPLICATION=true
REPLICATION_RETRY_SECONDS=30

# Security
ENCRYPTION_KEY_PATH=config/encryption.key
KEY_STORE_PATH=config/key_store.json

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### **Configuration Files**

- `config/settings.py`: Main configuration classes
- `.env`: Environment variables (create from `.env.example`)
- `config/key_store.json`: Encrypted key storage
- `config/encryption.key`: Encryption key file

## 🔄 Replication Architecture

### **Multi-Master Setup**

The system supports multi-master replication with:
- Automatic failover
- Conflict resolution
- Health monitoring
- Performance metrics

### **Replication Flow**

1. **Setup**: Configure nodes and credentials
2. **Initialize**: Create replication documents
3. **Monitor**: Track replication status
4. **Failover**: Handle node failures
5. **Recovery**: Restore failed nodes

### **Monitoring**

```bash
# Check cluster health
python scripts/monitor_cluster.py --health

# Get performance metrics
python scripts/monitor_cluster.py --metrics

# Monitor continuously
python scripts/monitor_cluster.py --watch
```

## 🛡️ Security Considerations

### **Authentication**
- CouchDB user authentication
- JWT token support (extensible)
- API key authentication (planned)

### **Encryption**
- Data encryption at rest
- TLS for data in transit
- Key rotation support

### **Authorization**
- Role-based access control
- Document-level permissions
- API endpoint protection

## 📊 Monitoring and Logging

### **Logging Strategy**
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation support

### **Health Checks**
- Application health endpoint
- Database connectivity checks
- Replication status monitoring
- Performance metrics collection

### **Alerting**
- Failed replication notifications
- Database connectivity alerts
- Performance degradation warnings

## 🔮 Extensibility

### **Adding New Features**

1. **API Endpoints**: Add routes in `api/app.py`
2. **Business Logic**: Create services in `services/`
3. **Data Models**: Define in `core/domain.py`
4. **Database Operations**: Add repositories in `database/`

### **Plugin Architecture**

The modular structure supports:
- Custom middleware
- Additional database backends
- External service integrations
- Custom authentication providers

## 📈 Performance Optimization

### **Database Performance**
- Connection pooling
- Query optimization
- Index management
- Replication tuning

### **Application Performance**
- Caching strategies
- Async processing
- Connection reuse
- Resource pooling

### **Monitoring Performance**
- Response time tracking
- Resource usage metrics
- Database query analysis
- Replication performance

This architecture provides a solid foundation for a scalable, maintainable GraphQL application with distributed replication capabilities.