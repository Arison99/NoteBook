import pytest
import os
import sys
import logging
from unittest.mock import Mock, patch

# Add the backend and src directories to Python path
backend_dir = os.path.dirname(os.path.dirname(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)
logging.getLogger('couchdb').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# Test fixtures that can be used across all test files
@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env_vars = {
        'COUCHDB_URL': 'http://test-couchdb:5984/',
        'COUCHDB_USER': 'test_admin',
        'COUCHDB_PASSWORD': 'test_password123',
        'REPLICATION_NODES': 'http://test-replica1:5984/,http://test-replica2:5984/',
        'REPLICATION_USER': 'test_admin',
        'REPLICATION_PASSWORD': 'test_password123',
        'CONTINUOUS_REPLICATION': 'true',
        'REPLICATION_FILTER': '',
        'REPLICATION_RETRY_SECONDS': '10',
        'FLASK_ENV': 'testing'
    }
    
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    yield test_env_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_couchdb_server():
    """Mock CouchDB server for testing"""
    server = Mock()
    server.version.return_value = "3.3.0"
    server.__contains__ = Mock(return_value=True)
    server.__getitem__ = Mock()
    server.create = Mock()
    return server


@pytest.fixture  
def mock_couchdb_database():
    """Mock CouchDB database for testing"""
    db = Mock()
    db.save = Mock()
    db.delete = Mock()
    db.__contains__ = Mock(return_value=True)
    db.__getitem__ = Mock()
    db.__setitem__ = Mock()
    db.__delitem__ = Mock()
    db.view = Mock()
    return db


@pytest.fixture
def sample_pdf_data():
    """Sample PDF data for testing"""
    # This is a minimal PDF structure encoded as base64
    return "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSANCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+Pgo+Pgo+PgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA5Mwo+PgpzdHJlYW0KQVQKL0YxIDEyIFRmCjcyIDcyMCBUZAooSGVsbG8gV29ybGQhKSBUago3MiA3MDggVGQKKFRoaXMgaXMgYSB0ZXN0IFBERi4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE3MyAwMDAwMCBuIAowMDAwMDAwMzc4IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNQovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNTMyCiUlRU9G"


@pytest.fixture
def sample_replication_status():
    """Sample replication status for testing"""
    return {
        "pdfs_to_replica1": {
            "state": "running",
            "source": "http://localhost:5984/pdfs",
            "target": "http://localhost:5985/pdfs", 
            "continuous": True,
            "last_updated": "2023-12-01T10:30:00Z",
            "docs_read": 150,
            "docs_written": 145,
            "doc_write_failures": 0,
            "revisions_checked": 200
        },
        "categories_to_replica1": {
            "state": "completed", 
            "source": "http://localhost:5984/categories",
            "target": "http://localhost:5985/categories",
            "continuous": False,
            "last_updated": "2023-12-01T09:15:00Z",
            "docs_read": 25,
            "docs_written": 25,
            "doc_write_failures": 0,
            "revisions_checked": 30
        },
        "analytics_failed_repl": {
            "state": "error",
            "source": "http://localhost:5984/analytics", 
            "target": "http://localhost:5986/analytics",
            "continuous": True,
            "last_updated": "2023-12-01T08:45:00Z",
            "error": "Connection refused"
        }
    }


@pytest.fixture
def sample_cluster_health():
    """Sample cluster health data for testing"""
    return {
        "http://localhost:5984/": {
            "status": "healthy",
            "version": "3.3.0", 
            "timestamp": "2023-12-01T10:30:00Z"
        },
        "http://localhost:5985/": {
            "status": "healthy",
            "version": "3.3.0",
            "timestamp": "2023-12-01T10:30:00Z"
        },
        "http://localhost:5986/": {
            "status": "unhealthy",
            "error": "Connection timeout",
            "timestamp": "2023-12-01T10:30:00Z"
        }
    }


@pytest.fixture
def mock_flask_app():
    """Mock Flask application for testing"""
    with patch('app.app') as mock_app:
        mock_app.config = {'TESTING': True}
        yield mock_app


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules before each test"""
    modules_to_reset = [
        'couchdb_client',
        'app'
    ]
    
    for module_name in modules_to_reset:
        if module_name in sys.modules:
            # Don't actually remove, just clear any cached state
            pass
    
    yield
    
    # Cleanup after test
    pass


# Helper functions for tests
def create_mock_response(data, status_code=200):
    """Create a mock HTTP response"""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = data
    response.text = str(data)
    response.raise_for_status = Mock()
    
    if status_code >= 400:
        from requests import HTTPError
        response.raise_for_status.side_effect = HTTPError(f"{status_code} Error")
    
    return response


def create_mock_couchdb_doc(doc_id, doc_data):
    """Create a mock CouchDB document"""
    doc = Mock()
    doc.id = doc_id
    doc['_id'] = doc_id
    doc['_rev'] = f"1-{hash(doc_id) % 1000000}"
    
    for key, value in doc_data.items():
        doc[key] = value
        
    return doc


# Pytest hooks for better test organization
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names and locations"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid or "test_deployment" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if "slow" in item.name or "timeout" in item.name:
            item.add_marker(pytest.mark.slow)
            
        # Mark network tests
        if "network" in item.name or "http" in item.name or "request" in item.name:
            item.add_marker(pytest.mark.network)
            
        # Mark docker tests
        if "docker" in item.name or "compose" in item.name:
            item.add_marker(pytest.mark.docker)


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Suppress warnings from third-party libraries during testing
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    
    # Set test-specific logging
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def pytest_sessionstart(session):
    """Actions to perform at the start of test session"""
    print("\n🧪 Starting NoteBook Backend Test Suite")
    print("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """Actions to perform at the end of test session"""
    print("\n" + "=" * 50)
    if exitstatus == 0:
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests finished with exit status: {exitstatus}")
    print("📊 Check coverage report in htmlcov/index.html")