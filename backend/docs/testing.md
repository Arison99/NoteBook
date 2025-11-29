# Testing Guide

This document provides comprehensive information about testing the NoteBook backend application.

## 📁 Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures and configuration
│   ├── unit/               # Fast unit tests
│   │   ├── __init__.py
│   │   ├── test_couchdb_client.py    # CouchDB replication manager tests
│   │   ├── test_app.py               # Flask API endpoint tests
│   │   └── test_monitor_cluster.py   # Monitoring script tests
│   └── integration/        # Slower integration tests
│       ├── __init__.py
│       └── test_deployment.py        # Docker & deployment tests
├── pytest.ini             # Pytest configuration
└── run_tests.py           # Test runner script
```

## 🚀 Quick Start

### Run All Tests
```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Skip slow tests
python run_tests.py --fast
```

### Run with Coverage
```bash
# Generate coverage report
python run_tests.py --coverage

# View HTML coverage report
# Open htmlcov/index.html in your browser
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)
Fast tests that don't require external dependencies:

- **`test_couchdb_client.py`**: Tests CouchDBReplicationManager class
  - Multi-node setup and configuration
  - Bidirectional replication logic
  - Health monitoring and failover
  - Error handling and retry mechanisms

- **`test_app.py`**: Tests Flask REST API endpoints
  - `/api/replication/status` - Get replication status
  - `/api/replication/health` - Check cluster health
  - `/api/replication/sync` - Manual synchronization
  - GraphQL endpoints and error handling

- **`test_monitor_cluster.py`**: Tests monitoring script
  - Cluster health checking
  - Performance metrics collection  
  - CLI argument processing
  - Report generation

### Integration Tests (`tests/integration/`)
Slower tests that may require external services:

- **`test_deployment.py`**: Tests deployment configuration
  - Docker Compose validation
  - HAProxy configuration testing
  - Environment variable validation
  - Container health checks

## 🏷️ Test Markers

Tests are automatically categorized with markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require Docker, etc.)
- `@pytest.mark.slow` - Tests that take more than 1 second
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.docker` - Tests requiring Docker

### Running Specific Markers
```bash
# Run only unit tests
pytest -m "unit"

# Run everything except integration tests
pytest -m "not integration"

# Run only network tests
pytest -m "network"

# Run only fast tests
pytest -m "not slow"
```

## 🎯 Coverage Requirements

- **Minimum Coverage**: 85%
- **Coverage Report**: Generated in `htmlcov/index.html`
- **Excluded from Coverage**:
  - Test files themselves
  - Virtual environment files
  - Migration files

### Coverage Commands
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# View coverage in terminal
pytest --cov=. --cov-report=term-missing

# Generate XML report (for CI/CD)
pytest --cov=. --cov-report=xml
```

## 🛠️ Test Configuration

### Environment Variables
Tests use these environment variables (set automatically in `conftest.py`):

```env
COUCHDB_URL=http://test-couchdb:5984/
COUCHDB_USER=test_admin
COUCHDB_PASSWORD=test_password123
REPLICATION_NODES=http://test-replica1:5984/,http://test-replica2:5984/
CONTINUOUS_REPLICATION=true
FLASK_ENV=testing
```

### Fixtures Available
- `test_environment` - Sets up test environment variables
- `mock_couchdb_server` - Mock CouchDB server for testing
- `mock_couchdb_database` - Mock CouchDB database
- `sample_pdf_data` - Sample PDF data for testing
- `sample_replication_status` - Mock replication status data
- `sample_cluster_health` - Mock cluster health data

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   
   # Install test dependencies
   pip install pytest pytest-cov requests-mock
   ```

2. **Path Issues**
   ```bash
   # Use absolute paths or run from backend directory
   python -m pytest tests/
   ```

3. **Missing Dependencies**
   ```bash
   # Install all requirements
   pip install -r requirements.txt
   
   # Install additional test dependencies
   pip install pytest pytest-cov requests-mock PyYAML
   ```

### Debugging Tests
```bash
# Run with verbose output
pytest -v

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run specific test function
pytest tests/unit/test_app.py::test_replication_status_endpoint -v
```

## 🔧 Writing New Tests

### Test File Structure
```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch

class TestExampleClass:
    """Test class for Example functionality"""
    
    def test_example_method(self, mock_dependency):
        """Test specific method functionality"""
        # Arrange
        expected_result = "expected"
        
        # Act
        result = example_function()
        
        # Assert
        assert result == expected_result

    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes a long time"""
        # Mark slow tests appropriately
        pass

    @pytest.mark.integration
    def test_database_integration(self):
        """Test database integration"""
        # Mark integration tests appropriately
        pass
```

### Best Practices
1. **Use descriptive test names**: `test_replication_handles_connection_timeout`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use appropriate markers**: `@pytest.mark.slow`, `@pytest.mark.integration`
4. **Mock external dependencies**: Use `unittest.mock` for external services
5. **Use fixtures**: Share common test setup using `conftest.py`

## 📊 CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v1
        with:
          file: ./backend/coverage.xml
```

## 📈 Monitoring Test Quality

- **Coverage Target**: Maintain 85%+ coverage
- **Test Performance**: Unit tests should complete in <5 seconds
- **Integration Tests**: Should complete in <30 seconds
- **Test Reliability**: Tests should pass consistently (no flaky tests)

Run `python run_tests.py --coverage --verbose` regularly to monitor test health!