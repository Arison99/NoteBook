import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import couchdb
from couchdb_client import CouchDBReplicationManager, get_or_create_db, setup_replication


class TestCouchDBReplicationManager:
    """Test the CouchDBReplicationManager class"""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock CouchDB server"""
        server = Mock()
        server.version.return_value = "3.3.0"
        server.__contains__ = Mock(return_value=False)
        server.create = Mock()
        return server
    
    @pytest.fixture
    def replication_manager(self, mock_server):
        """Create a CouchDBReplicationManager instance with mocked servers"""
        with patch('couchdb.Server') as mock_server_class:
            mock_server_class.return_value = mock_server
            manager = CouchDBReplicationManager(
                primary_url="http://localhost:5984/",
                nodes=["http://localhost:5985/", "http://localhost:5986/"],
                user="admin",
                password="password"
            )
            return manager
    
    def test_initialization(self):
        """Test manager initialization"""
        with patch('couchdb.Server') as mock_server_class:
            mock_server = Mock()
            mock_server.version.return_value = "3.3.0"
            mock_server_class.return_value = mock_server
            
            manager = CouchDBReplicationManager(
                primary_url="http://localhost:5984/",
                nodes=["http://localhost:5985/", "http://localhost:5986/"],
                user="admin",
                password="password"
            )
            
            assert manager.primary_url == "http://localhost:5984/"
            assert len(manager.nodes) == 2
            assert manager.user == "admin"
            assert manager.password == "password"
    
    def test_initialization_with_connection_failure(self):
        """Test initialization when some nodes fail to connect"""
        with patch('couchdb.Server') as mock_server_class:
            # First call (primary) succeeds, second fails, third succeeds
            mock_primary = Mock()
            mock_primary.version.return_value = "3.3.0"
            
            mock_failing = Mock()
            mock_failing.version.side_effect = Exception("Connection failed")
            
            mock_working = Mock()
            mock_working.version.return_value = "3.3.0"
            
            mock_server_class.side_effect = [mock_primary, mock_failing, mock_working]
            
            manager = CouchDBReplicationManager(
                primary_url="http://localhost:5984/",
                nodes=["http://localhost:5985/", "http://localhost:5986/"],
                user="admin",
                password="password"
            )
            
            # Should only have one working replication server
            assert len(manager.replication_servers) == 1
            assert "http://localhost:5986/" in manager.replication_servers
    
    def test_get_primary_db_existing(self, replication_manager, mock_server):
        """Test getting an existing database"""
        mock_server.__contains__.return_value = True
        mock_db = Mock()
        mock_server.__getitem__.return_value = mock_db
        
        db = replication_manager.get_primary_db("test_db")
        
        assert db == mock_db
        mock_server.__contains__.assert_called_with("test_db")
    
    def test_get_primary_db_create_new(self, replication_manager, mock_server):
        """Test creating a new database"""
        mock_server.__contains__.return_value = False
        mock_db = Mock()
        mock_server.create.return_value = mock_db
        
        db = replication_manager.get_primary_db("test_db")
        
        assert db == mock_db
        mock_server.create.assert_called_with("test_db")
    
    def test_setup_database_replication_success(self, replication_manager):
        """Test successful database replication setup"""
        # Mock the replication servers
        mock_server1 = Mock()
        mock_server1.__contains__.return_value = False
        mock_server1.create.return_value = Mock()
        
        mock_server2 = Mock()
        mock_server2.__contains__.return_value = False
        mock_server2.create.return_value = Mock()
        
        replication_manager.replication_servers = {
            "http://localhost:5985/": mock_server1,
            "http://localhost:5986/": mock_server2
        }
        
        # Mock the _create_replication method
        with patch.object(replication_manager, '_create_replication') as mock_create_repl:
            results = replication_manager.setup_database_replication("test_db")
            
            # Should have results for both nodes
            assert len(results) == 2
            assert all(results.values())  # All should be True
            
            # Should create 4 replications (bidirectional for 2 nodes)
            assert mock_create_repl.call_count == 4
    
    def test_setup_database_replication_failure(self, replication_manager):
        """Test database replication setup with failures"""
        # Mock one server failing to create database
        mock_server1 = Mock()
        mock_server1.__contains__.return_value = False
        mock_server1.create.side_effect = Exception("Database creation failed")
        
        replication_manager.replication_servers = {
            "http://localhost:5985/": mock_server1
        }
        
        results = replication_manager.setup_database_replication("test_db")
        
        # Should have result for the failing node
        assert len(results) == 1
        assert not results["http://localhost:5985/"]
    
    def test_create_replication_new(self, replication_manager):
        """Test creating a new replication document"""
        # Mock the _replicator database
        mock_replicator_db = Mock()
        mock_replicator_db.__getitem__.side_effect = couchdb.ResourceNotFound()
        
        with patch.object(replication_manager, 'get_or_create_db', return_value=mock_replicator_db):
            replication_manager._create_replication(
                source="http://localhost:5984/test",
                target="http://localhost:5985/test",
                replication_id="test_replication",
                continuous=True
            )
            
            # Should set the replication document
            mock_replicator_db.__setitem__.assert_called_once()
            args = mock_replicator_db.__setitem__.call_args
            assert args[0][0] == "test_replication"  # replication_id
            
            repl_doc = args[0][1]  # replication document
            assert repl_doc["source"]["url"] == "http://localhost:5984/test"
            assert repl_doc["target"]["url"] == "http://localhost:5985/test"
            assert repl_doc["continuous"] is True
    
    def test_create_replication_update_existing(self, replication_manager):
        """Test updating an existing replication document"""
        # Mock the _replicator database with existing document
        mock_replicator_db = Mock()
        existing_doc = {"_id": "test_replication", "_rev": "1-abc123"}
        mock_replicator_db.__getitem__.return_value = existing_doc
        
        with patch.object(replication_manager, 'get_or_create_db', return_value=mock_replicator_db):
            replication_manager._create_replication(
                source="http://localhost:5984/test",
                target="http://localhost:5985/test",
                replication_id="test_replication",
                continuous=True
            )
            
            # Should update the existing document
            mock_replicator_db.__setitem__.assert_called_once()
            args = mock_replicator_db.__setitem__.call_args
            repl_doc = args[0][1]
            assert repl_doc["_rev"] == "1-abc123"
    
    def test_get_replication_status_success(self, replication_manager):
        """Test getting replication status successfully"""
        # Mock the _replicator database
        mock_replicator_db = Mock()
        mock_replicator_db.__iter__.return_value = ["repl1", "repl2", "_design/test"]
        
        mock_doc1 = {
            "_id": "repl1",
            "_replication_state": "running",
            "source": {"url": "http://localhost:5984/test"},
            "target": {"url": "http://localhost:5985/test"},
            "continuous": True,
            "_replication_stats": {
                "docs_read": 100,
                "docs_written": 95,
                "doc_write_failures": 0
            }
        }
        
        mock_doc2 = {
            "_id": "repl2",
            "_replication_state": "completed",
            "source": {"url": "http://localhost:5985/test"},
            "target": {"url": localhost:5984/test"},
            "continuous": False
        }
        
        mock_replicator_db.__getitem__.side_effect = lambda x: mock_doc1 if x == "repl1" else mock_doc2
        
        with patch.object(replication_manager.primary_server, '__getitem__', return_value=mock_replicator_db):
            status = replication_manager.get_replication_status()
            
            assert len(status) == 2
            assert status["repl1"]["state"] == "running"
            assert status["repl1"]["docs_read"] == 100
            assert status["repl2"]["state"] == "completed"
    
    def test_get_replication_status_with_database_filter(self, replication_manager):
        """Test getting replication status filtered by database"""
        mock_replicator_db = Mock()
        mock_replicator_db.__iter__.return_value = ["test_db_repl1", "other_db_repl1"]
        
        mock_doc = {
            "_id": "test_db_repl1",
            "_replication_state": "running",
            "source": {"url": "http://localhost:5984/test_db"},
            "target": {"url": "http://localhost:5985/test_db"},
            "continuous": True
        }
        
        mock_replicator_db.__getitem__.return_value = mock_doc
        
        with patch.object(replication_manager.primary_server, '__getitem__', return_value=mock_replicator_db):
            status = replication_manager.get_replication_status("test_db")
            
            # Should only return replications containing "test_db"
            assert len(status) == 1
            assert "test_db_repl1" in status
    
    def test_stop_replication_success(self, replication_manager):
        """Test stopping a replication successfully"""
        mock_replicator_db = Mock()
        mock_doc = Mock()
        mock_doc.id = "test_replication"
        mock_replicator_db.__getitem__.return_value = mock_doc
        
        with patch.object(replication_manager.primary_server, '__getitem__', return_value=mock_replicator_db):
            result = replication_manager.stop_replication("test_replication")
            
            assert result is True
            mock_replicator_db.__delitem__.assert_called_once_with("test_replication")
    
    def test_stop_replication_failure(self, replication_manager):
        """Test stopping a replication with failure"""
        mock_replicator_db = Mock()
        mock_replicator_db.__getitem__.side_effect = Exception("Replication not found")
        
        with patch.object(replication_manager.primary_server, '__getitem__', return_value=mock_replicator_db):
            result = replication_manager.stop_replication("test_replication")
            
            assert result is False
    
    def test_check_node_health_all_healthy(self, replication_manager):
        """Test checking node health when all nodes are healthy"""
        # Mock primary server health
        replication_manager.primary_server.version.return_value = "3.3.0"
        
        # Mock replication servers health
        mock_server1 = Mock()
        mock_server1.version.return_value = "3.3.0"
        mock_server2 = Mock()
        mock_server2.version.return_value = "3.2.0"
        
        replication_manager.replication_servers = {
            "http://localhost:5985/": mock_server1,
            "http://localhost:5986/": mock_server2
        }
        
        health = replication_manager.check_node_health()
        
        assert len(health) == 3
        assert all(node["status"] == "healthy" for node in health.values())
        assert health["http://localhost:5984/"]["version"] == "3.3.0"
        assert health["http://localhost:5985/"]["version"] == "3.3.0"
        assert health["http://localhost:5986/"]["version"] == "3.2.0"
    
    def test_check_node_health_with_failures(self, replication_manager):
        """Test checking node health with some nodes failing"""
        # Mock primary server as healthy
        replication_manager.primary_server.version.return_value = "3.3.0"
        
        # Mock one healthy and one failing replication server
        mock_server1 = Mock()
        mock_server1.version.return_value = "3.3.0"
        mock_server2 = Mock()
        mock_server2.version.side_effect = Exception("Connection timeout")
        
        replication_manager.replication_servers = {
            "http://localhost:5985/": mock_server1,
            "http://localhost:5986/": mock_server2
        }
        
        health = replication_manager.check_node_health()
        
        assert len(health) == 3
        assert health["http://localhost:5984/"]["status"] == "healthy"
        assert health["http://localhost:5985/"]["status"] == "healthy"
        assert health["http://localhost:5986/"]["status"] == "unhealthy"
        assert "Connection timeout" in health["http://localhost:5986/"]["error"]
    
    def test_perform_failover(self, replication_manager):
        """Test performing failover for a failed node"""
        # Mock replication status
        mock_replications = {
            "failed_node_repl": {
                "source": "http://failed-node:5984/test",
                "target": "http://localhost:5984/test"
            },
            "healthy_repl": {
                "source": "http://localhost:5984/test",
                "target": "http://healthy-node:5984/test"
            }
        }
        
        with patch.object(replication_manager, 'get_replication_status', return_value=mock_replications):
            with patch.object(replication_manager, 'stop_replication', return_value=True) as mock_stop:
                # Add failed node to active servers first
                replication_manager.replication_servers["http://failed-node:5984/"] = Mock()
                
                result = replication_manager.perform_failover("http://failed-node:5984/", "test")
                
                assert result is True
                mock_stop.assert_called_once_with("failed_node_repl")
                assert "http://failed-node:5984/" not in replication_manager.replication_servers
    
    def test_sync_database_success(self, replication_manager):
        """Test successful database sync"""
        mock_server1 = Mock()
        mock_server2 = Mock()
        
        replication_manager.replication_servers = {
            "http://localhost:5985/": mock_server1,
            "http://localhost:5986/": mock_server2
        }
        
        with patch.object(replication_manager, '_create_replication') as mock_create_repl:
            results = replication_manager.sync_database("test_db", wait_for_completion=False)
            
            assert len(results) == 2
            assert all(results.values())  # All should be True
            
            # Should create one-time replications
            assert mock_create_repl.call_count == 2
            
            # Check that continuous=False for sync replications
            for call in mock_create_repl.call_args_list:
                assert call[1]["continuous"] is False


class TestModuleLevelFunctions:
    """Test module-level functions in couchdb_client"""
    
    def test_get_or_create_db_without_replication(self):
        """Test get_or_create_db when replication is not configured"""
        with patch('couchdb_client.replication_manager', None):
            with patch('couchdb_client.server') as mock_server:
                mock_server.__contains__.return_value = True
                mock_db = Mock()
                mock_server.__getitem__.return_value = mock_db
                
                db = get_or_create_db("test_db")
                
                assert db == mock_db
                mock_server.__contains__.assert_called_with("test_db")
    
    def test_get_or_create_db_with_replication_existing(self):
        """Test get_or_create_db with replication for existing database"""
        mock_manager = Mock()
        mock_db = Mock()
        mock_manager.get_primary_db.return_value = mock_db
        
        with patch('couchdb_client.replication_manager', mock_manager):
            with patch('couchdb_client.server') as mock_server:
                mock_server.__contains__.return_value = True
                
                db = get_or_create_db("test_db")
                
                assert db == mock_db
                mock_manager.get_primary_db.assert_called_with("test_db")
                # Should not setup replication for existing DB
                mock_manager.setup_database_replication.assert_not_called()
    
    def test_get_or_create_db_with_replication_new(self):
        """Test get_or_create_db with replication for new database"""
        mock_manager = Mock()
        mock_db = Mock()
        mock_manager.get_primary_db.return_value = mock_db
        mock_manager.setup_database_replication.return_value = {"node1": True}
        
        with patch('couchdb_client.replication_manager', mock_manager):
            with patch('couchdb_client.server') as mock_server:
                mock_server.__contains__.return_value = False
                
                db = get_or_create_db("test_db")
                
                assert db == mock_db
                mock_manager.get_primary_db.assert_called_with("test_db")
                # Should setup replication for new DB
                mock_manager.setup_database_replication.assert_called_with("test_db")
    
    def test_setup_replication_without_manager(self):
        """Test setup_replication when no manager is configured"""
        with patch('couchdb_client.replication_manager', None):
            result = setup_replication("test_db")
            
            assert result == {}
    
    def test_setup_replication_with_manager(self):
        """Test setup_replication with manager"""
        mock_manager = Mock()
        mock_manager.setup_database_replication.return_value = {"node1": True, "node2": True}
        
        with patch('couchdb_client.replication_manager', mock_manager):
            result = setup_replication("test_db", bidirectional=False)
            
            assert result == {"node1": True, "node2": True}
            mock_manager.setup_database_replication.assert_called_with("test_db", False)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_nodes_list(self):
        """Test initialization with empty nodes list"""
        with patch('couchdb.Server') as mock_server_class:
            mock_server = Mock()
            mock_server.version.return_value = "3.3.0"
            mock_server_class.return_value = mock_server
            
            manager = CouchDBReplicationManager(
                primary_url="http://localhost:5984/",
                nodes=[],
                user="admin",
                password="password"
            )
            
            assert len(manager.nodes) == 0
            assert len(manager.replication_servers) == 0
    
    def test_whitespace_in_nodes(self):
        """Test nodes list with whitespace"""
        with patch('couchdb.Server') as mock_server_class:
            mock_server = Mock()
            mock_server.version.return_value = "3.3.0"
            mock_server_class.return_value = mock_server
            
            manager = CouchDBReplicationManager(
                primary_url="http://localhost:5984/",
                nodes=["  http://localhost:5985/  ", "", "http://localhost:5986/"],
                user="admin",
                password="password"
            )
            
            # Should filter out empty strings and strip whitespace
            assert len(manager.nodes) == 2
            assert "http://localhost:5985/" in manager.nodes
            assert "http://localhost:5986/" in manager.nodes
    
    def test_replication_with_filter(self):
        """Test replication creation with filter"""
        with patch('couchdb_client.REPLICATION_FILTER', 'test_filter'):
            with patch('couchdb.Server') as mock_server_class:
                mock_server = Mock()
                mock_server.version.return_value = "3.3.0"
                mock_server_class.return_value = mock_server
                
                manager = CouchDBReplicationManager(
                    primary_url="http://localhost:5984/",
                    nodes=["http://localhost:5985/"],
                    user="admin",
                    password="password"
                )
                
                mock_replicator_db = Mock()
                mock_replicator_db.__getitem__.side_effect = couchdb.ResourceNotFound()
                
                with patch.object(manager, 'get_or_create_db', return_value=mock_replicator_db):
                    manager._create_replication(
                        source="http://localhost:5984/test",
                        target="http://localhost:5985/test",
                        replication_id="test_replication",
                        continuous=True
                    )
                    
                    # Check that filter was added to replication document
                    args = mock_replicator_db.__setitem__.call_args
                    repl_doc = args[0][1]
                    assert repl_doc["filter"] == "test_filter"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ['COUCHDB_URL'] = 'http://localhost:5984/'
    os.environ['COUCHDB_USER'] = 'test_admin'
    os.environ['COUCHDB_PASSWORD'] = 'test_password'
    os.environ['REPLICATION_NODES'] = 'http://localhost:5985/,http://localhost:5986/'
    os.environ['CONTINUOUS_REPLICATION'] = 'true'
    os.environ['REPLICATION_RETRY_SECONDS'] = '10'