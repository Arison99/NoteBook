import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import requests
import tempfile
import os

# Import the Flask app
from app import app


class TestReplicationEndpoints:
    """Test Flask app replication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_replication_manager(self):
        """Mock the replication manager"""
        with patch('app.replication_manager') as mock_manager:
            yield mock_manager
    
    def test_replication_status_success(self, client, mock_replication_manager):
        """Test successful replication status retrieval"""
        mock_status = {
            "repl1": {
                "state": "running",
                "source": "http://localhost:5984/test",
                "target": "http://localhost:5985/test",
                "continuous": True,
                "docs_read": 100,
                "docs_written": 95
            }
        }
        
        with patch('app.get_replication_status', return_value=mock_status):
            response = client.get('/api/replication/status')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['replications'] == mock_status
            assert 'timestamp' in data
    
    def test_replication_status_with_database_filter(self, client, mock_replication_manager):
        """Test replication status with database filter"""
        mock_status = {
            "pdfs_repl": {
                "state": "running",
                "source": "http://localhost:5984/pdfs",
                "target": "http://localhost:5985/pdfs",
                "continuous": True
            }
        }
        
        with patch('app.get_replication_status', return_value=mock_status) as mock_get_status:
            response = client.get('/api/replication/status?database=pdfs')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['replications'] == mock_status
            mock_get_status.assert_called_with('pdfs')
    
    def test_replication_status_error(self, client, mock_replication_manager):
        """Test replication status with error"""
        with patch('app.get_replication_status', side_effect=Exception("Database connection failed")):
            response = client.get('/api/replication/status')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database connection failed' in data['error']
    
    def test_cluster_health_success(self, client, mock_replication_manager):
        """Test successful cluster health check"""
        mock_health = {
            "http://localhost:5984/": {
                "status": "healthy",
                "version": "3.3.0"
            },
            "http://localhost:5985/": {
                "status": "healthy",
                "version": "3.3.0"
            }
        }
        
        with patch('app.check_cluster_health', return_value=mock_health):
            response = client.get('/api/replication/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['nodes'] == mock_health
            assert 'timestamp' in data
    
    def test_cluster_health_error(self, client, mock_replication_manager):
        """Test cluster health check with error"""
        with patch('app.check_cluster_health', side_effect=Exception("Network error")):
            response = client.get('/api/replication/health')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Network error' in data['error']
    
    def test_sync_database_success(self, client, mock_replication_manager):
        """Test successful database sync"""
        mock_results = {
            "http://localhost:5985/": True,
            "http://localhost:5986/": True
        }
        
        with patch('app.sync_database', return_value=mock_results):
            response = client.post('/api/replication/sync',
                                 json={'database': 'test_db', 'wait': True})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['database'] == 'test_db'
            assert data['results'] == mock_results
    
    def test_sync_database_missing_database(self, client, mock_replication_manager):
        """Test sync database without database parameter"""
        response = client.post('/api/replication/sync', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Database name is required' in data['error']
    
    def test_sync_database_error(self, client, mock_replication_manager):
        """Test sync database with error"""
        with patch('app.sync_database', side_effect=Exception("Sync failed")):
            response = client.post('/api/replication/sync',
                                 json={'database': 'test_db'})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Sync failed' in data['error']
    
    def test_setup_database_replication_success(self, client, mock_replication_manager):
        """Test successful database replication setup"""
        mock_results = {
            "http://localhost:5985/": True,
            "http://localhost:5986/": True
        }
        
        with patch('app.setup_replication', return_value=mock_results):
            response = client.post('/api/replication/setup',
                                 json={'database': 'new_db', 'bidirectional': False})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['database'] == 'new_db'
            assert data['bidirectional'] is False
            assert data['results'] == mock_results
    
    def test_setup_database_replication_missing_database(self, client, mock_replication_manager):
        """Test setup replication without database parameter"""
        response = client.post('/api/replication/setup', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Database name is required' in data['error']
    
    def test_setup_database_replication_default_bidirectional(self, client, mock_replication_manager):
        """Test setup replication with default bidirectional value"""
        mock_results = {"http://localhost:5985/": True}
        
        with patch('app.setup_replication', return_value=mock_results) as mock_setup:
            response = client.post('/api/replication/setup',
                                 json={'database': 'test_db'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['bidirectional'] is True
            mock_setup.assert_called_with('test_db', True)
    
    def test_replication_info_success(self, client):
        """Test successful replication info retrieval"""
        with patch.dict(os.environ, {
            'COUCHDB_URL': 'http://test:5984/',
            'REPLICATION_NODES': 'http://node1:5984/,http://node2:5984/',
            'CONTINUOUS_REPLICATION': 'true',
            'REPLICATION_RETRY_SECONDS': '60'
        }):
            with patch('app.replication_manager', Mock()):
                response = client.get('/api/replication/info')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                
                info = data['info']
                assert info['replication_enabled'] is True
                assert info['primary_url'] == 'http://test:5984/'
                assert len(info['replication_nodes']) == 2
                assert info['continuous_replication'] is True
                assert info['retry_seconds'] == 60
    
    def test_replication_info_no_replication(self, client):
        """Test replication info when replication is disabled"""
        with patch('app.replication_manager', None):
            response = client.get('/api/replication/info')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['info']['replication_enabled'] is False
    
    def test_app_health_success(self, client):
        """Test successful health check"""
        mock_cluster_health = {
            "http://localhost:5984/": {"status": "healthy"},
            "http://localhost:5985/": {"status": "healthy"}
        }
        
        with patch('app.check_cluster_health', return_value=mock_cluster_health):
            with patch('app.replication_manager', Mock()):
                response = client.get('/api/health')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'healthy'
                assert data['replication_enabled'] is True
                assert 'database_cluster' in data
                assert 'timestamp' in data
    
    def test_app_health_no_replication(self, client):
        """Test health check without replication"""
        with patch('app.replication_manager', None):
            response = client.get('/api/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['replication_enabled'] is False
            assert data['database_cluster']['single_node'] is True
    
    def test_app_health_error(self, client):
        """Test health check with error"""
        with patch('app.check_cluster_health', side_effect=Exception("Health check failed")):
            response = client.get('/api/health')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert 'Health check failed' in data['error']
    
    def test_graphql_endpoint_still_works(self, client):
        """Test that GraphQL endpoint still works after replication changes"""
        # Mock GraphQL execution
        with patch('app.graphql_sync') as mock_graphql:
            mock_graphql.return_value = (True, {"data": {"test": "result"}})
            
            response = client.post('/graphql',
                                 json={"query": "{ test }"})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["data"]["test"] == "result"
            mock_graphql.assert_called_once()


class TestReplicationEndpointsIntegration:
    """Integration tests for replication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_full_replication_workflow(self, client):
        """Test a full replication workflow"""
        # Mock all dependencies
        mock_manager = Mock()
        mock_setup_results = {"http://localhost:5985/": True}
        mock_status = {
            "test_db_repl": {
                "state": "running",
                "source": "http://localhost:5984/test_db",
                "target": "http://localhost:5985/test_db"
            }
        }
        mock_sync_results = {"http://localhost:5985/": True}
        
        with patch('app.replication_manager', mock_manager):
            with patch('app.setup_replication', return_value=mock_setup_results):
                with patch('app.get_replication_status', return_value=mock_status):
                    with patch('app.sync_database', return_value=mock_sync_results):
                        
                        # 1. Setup replication for new database
                        response = client.post('/api/replication/setup',
                                             json={'database': 'test_db'})
                        assert response.status_code == 200
                        
                        # 2. Check replication status
                        response = client.get('/api/replication/status?database=test_db')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert 'test_db_repl' in data['replications']
                        
                        # 3. Force sync
                        response = client.post('/api/replication/sync',
                                             json={'database': 'test_db'})
                        assert response.status_code == 200
                        
                        # 4. Check overall health
                        with patch('app.check_cluster_health', return_value={"node1": {"status": "healthy"}}):
                            response = client.get('/api/health')
                            assert response.status_code == 200


class TestConfigurationHandling:
    """Test configuration and environment handling"""
    
    def test_environment_variable_parsing(self):
        """Test parsing of environment variables"""
        with patch.dict(os.environ, {
            'REPLICATION_NODES': 'http://node1:5984/,http://node2:5984/,http://node3:5984/',
            'CONTINUOUS_REPLICATION': 'false',
            'REPLICATION_RETRY_SECONDS': '45'
        }):
            # Re-import to get updated environment
            import importlib
            import couchdb_client
            importlib.reload(couchdb_client)
            
            from couchdb_client import REPLICATION_NODES, CONTINUOUS_REPLICATION, REPLICATION_RETRY_SECONDS
            
            assert len(REPLICATION_NODES) == 3
            assert 'http://node1:5984/' in REPLICATION_NODES
            assert CONTINUOUS_REPLICATION is False
            assert REPLICATION_RETRY_SECONDS == 45
    
    def test_empty_replication_nodes(self):
        """Test behavior with empty replication nodes"""
        with patch.dict(os.environ, {'REPLICATION_NODES': ''}):
            import importlib
            import couchdb_client
            importlib.reload(couchdb_client)
            
            from couchdb_client import REPLICATION_NODES
            assert REPLICATION_NODES == []


@pytest.fixture(scope="function", autouse=True)
def reset_environment():
    """Reset environment variables before each test"""
    # Store original values
    original_env = {}
    env_vars = [
        'COUCHDB_URL', 'COUCHDB_USER', 'COUCHDB_PASSWORD',
        'REPLICATION_NODES', 'CONTINUOUS_REPLICATION', 'REPLICATION_RETRY_SECONDS'
    ]
    
    for var in env_vars:
        original_env[var] = os.environ.get(var)
    
    yield
    
    # Restore original values
    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]