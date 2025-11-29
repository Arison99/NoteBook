import pytest
import json
import requests
from unittest.mock import Mock, patch, call
from monitor_cluster import CouchDBMonitor


class TestCouchDBMonitor:
    """Test the CouchDBMonitor class"""
    
    @pytest.fixture
    def monitor(self):
        """Create a CouchDBMonitor instance"""
        return CouchDBMonitor("http://localhost:5000")
    
    @pytest.fixture
    def mock_session(self):
        """Mock requests session"""
        with patch('monitor_cluster.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            yield mock_session
    
    def test_initialization(self):
        """Test monitor initialization"""
        monitor = CouchDBMonitor("http://localhost:5000/")
        assert monitor.backend_url == "http://localhost:5000"
    
    def test_initialization_strips_trailing_slash(self):
        """Test that trailing slash is stripped from URL"""
        monitor = CouchDBMonitor("http://localhost:5000/")
        assert monitor.backend_url == "http://localhost:5000"
    
    def test_get_cluster_health_success(self, monitor):
        """Test successful cluster health retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "nodes": {
                "http://localhost:5984/": {"status": "healthy"},
                "http://localhost:5985/": {"status": "healthy"}
            }
        }
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_cluster_health()
            
            assert result["success"] is True
            assert len(result["nodes"]) == 2
            monitor.session.get.assert_called_once_with("http://localhost:5000/api/replication/health")
    
    def test_get_cluster_health_error(self, monitor):
        """Test cluster health retrieval with error"""
        with patch.object(monitor.session, 'get', side_effect=requests.RequestException("Connection failed")):
            result = monitor.get_cluster_health()
            
            assert result["success"] is False
            assert "Connection failed" in result["error"]
    
    def test_get_replication_status_success(self, monitor):
        """Test successful replication status retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "replications": {
                "repl1": {"state": "running"},
                "repl2": {"state": "completed"}
            }
        }
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_replication_status()
            
            assert result["success"] is True
            assert len(result["replications"]) == 2
            monitor.session.get.assert_called_once_with("http://localhost:5000/api/replication/status")
    
    def test_get_replication_status_with_database(self, monitor):
        """Test replication status retrieval with database filter"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "replications": {}}
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            monitor.get_replication_status("test_db")
            
            monitor.session.get.assert_called_once_with("http://localhost:5000/api/replication/status?database=test_db")
    
    def test_get_app_health_success(self, monitor):
        """Test successful app health check"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "replication_enabled": True
        }
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_app_health()
            
            assert result["status"] == "healthy"
            monitor.session.get.assert_called_once_with("http://localhost:5000/api/health")
    
    def test_get_replication_info_success(self, monitor):
        """Test successful replication info retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "info": {
                "replication_enabled": True,
                "primary_url": "http://localhost:5984/"
            }
        }
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_replication_info()
            
            assert result["success"] is True
            assert result["info"]["replication_enabled"] is True
    
    def test_sync_database_success(self, monitor):
        """Test successful database sync"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "database": "test_db",
            "results": {"node1": True}
        }
        
        with patch.object(monitor.session, 'post', return_value=mock_response):
            result = monitor.sync_database("test_db", wait=True)
            
            assert result["success"] is True
            assert result["database"] == "test_db"
            monitor.session.post.assert_called_once_with(
                "http://localhost:5000/api/replication/sync",
                json={"database": "test_db", "wait": True}
            )
    
    def test_sync_database_error(self, monitor):
        """Test database sync with error"""
        with patch.object(monitor.session, 'post', side_effect=requests.RequestException("Sync failed")):
            result = monitor.sync_database("test_db")
            
            assert result["success"] is False
            assert "Sync failed" in result["error"]
    
    def test_print_health_summary_healthy_cluster(self, monitor, capsys):
        """Test printing health summary for healthy cluster"""
        # Mock all the API calls
        app_health = {"status": "healthy"}
        repl_info = {
            "success": True,
            "info": {
                "replication_enabled": True,
                "primary_url": "http://localhost:5984/",
                "replication_nodes": ["http://localhost:5985/"],
                "continuous_replication": True,
                "retry_seconds": 30
            }
        }
        cluster_health = {
            "success": True,
            "nodes": {
                "http://localhost:5984/": {"status": "healthy", "version": "3.3.0"},
                "http://localhost:5985/": {"status": "healthy", "version": "3.3.0"}
            }
        }
        repl_status = {
            "success": True,
            "replications": {
                "test_repl": {
                    "state": "running",
                    "source": "http://localhost:5984/test",
                    "target": "http://localhost:5985/test",
                    "docs_read": 100,
                    "docs_written": 95,
                    "doc_write_failures": 0
                }
            }
        }
        
        with patch.object(monitor, 'get_app_health', return_value=app_health):
            with patch.object(monitor, 'get_replication_info', return_value=repl_info):
                with patch.object(monitor, 'get_cluster_health', return_value=cluster_health):
                    with patch.object(monitor, 'get_replication_status', return_value=repl_status):
                        monitor.print_health_summary()
        
        captured = capsys.readouterr()
        assert "✅ Application: HEALTHY" in captured.out
        assert "✅ YES" in captured.out  # Replication enabled
        assert "2/2 nodes healthy" in captured.out
        assert "✅ test_repl" in captured.out
    
    def test_print_health_summary_unhealthy_cluster(self, monitor, capsys):
        """Test printing health summary for unhealthy cluster"""
        app_health = {"status": "unhealthy", "error": "Database connection failed"}
        repl_info = {"success": False, "error": "Config error"}
        cluster_health = {
            "success": True,
            "nodes": {
                "http://localhost:5984/": {"status": "healthy", "version": "3.3.0"},
                "http://localhost:5985/": {"status": "unhealthy", "error": "Connection timeout"}
            }
        }
        repl_status = {"success": False, "error": "Replication error"}
        
        with patch.object(monitor, 'get_app_health', return_value=app_health):
            with patch.object(monitor, 'get_replication_info', return_value=repl_info):
                with patch.object(monitor, 'get_cluster_health', return_value=cluster_health):
                    with patch.object(monitor, 'get_replication_status', return_value=repl_status):
                        monitor.print_health_summary()
        
        captured = capsys.readouterr()
        assert "❌ Application: UNHEALTHY" in captured.out
        assert "Database connection failed" in captured.out
        assert "1/2 nodes healthy" in captured.out
        assert "❌ Failed to get replication status" in captured.out
    
    def test_check_database_replication_success(self, monitor, capsys):
        """Test checking replication for specific database"""
        repl_status = {
            "success": True,
            "replications": {
                "test_db_repl": {
                    "state": "running",
                    "continuous": True,
                    "last_updated": "2023-01-01T00:00:00Z",
                    "docs_read": 100,
                    "docs_written": 95,
                    "revisions_checked": 150,
                    "doc_write_failures": 2
                }
            }
        }
        
        with patch.object(monitor, 'get_replication_status', return_value=repl_status):
            monitor.check_database_replication("test_db")
        
        captured = capsys.readouterr()
        assert "Checking replication for database: test_db" in captured.out
        assert "Replication: test_db_repl" in captured.out
        assert "State: running" in captured.out
        assert "Documents Read: 100" in captured.out
        assert "⚠️ Write Failures: 2" in captured.out
    
    def test_check_database_replication_no_replications(self, monitor, capsys):
        """Test checking replication when no replications exist"""
        repl_status = {"success": True, "replications": {}}
        
        with patch.object(monitor, 'get_replication_status', return_value=repl_status):
            monitor.check_database_replication("test_db")
        
        captured = capsys.readouterr()
        assert "No replications found for database: test_db" in captured.out
    
    def test_check_database_replication_error(self, monitor, capsys):
        """Test checking replication with error"""
        repl_status = {"success": False, "error": "Connection failed"}
        
        with patch.object(monitor, 'get_replication_status', return_value=repl_status):
            monitor.check_database_replication("test_db")
        
        captured = capsys.readouterr()
        assert "Error: Connection failed" in captured.out
    
    def test_monitor_continuous_keyboard_interrupt(self, monitor, capsys):
        """Test continuous monitoring with keyboard interrupt"""
        with patch.object(monitor, 'print_health_summary'):
            with patch('monitor_cluster.time.sleep', side_effect=KeyboardInterrupt):
                monitor.monitor_continuous(1)
        
        captured = capsys.readouterr()
        assert "Starting continuous monitoring" in captured.out
        assert "Monitoring stopped by user" in captured.out


class TestCLIInterface:
    """Test command line interface"""
    
    def test_main_default_health_summary(self, capsys):
        """Test main function with default behavior (health summary)"""
        mock_monitor = Mock()
        
        with patch('monitor_cluster.CouchDBMonitor', return_value=mock_monitor):
            with patch('sys.argv', ['monitor_cluster.py']):
                from monitor_cluster import main
                main()
        
        mock_monitor.print_health_summary.assert_called_once()
    
    def test_main_with_database_check(self, capsys):
        """Test main function with database-specific check"""
        mock_monitor = Mock()
        
        with patch('monitor_cluster.CouchDBMonitor', return_value=mock_monitor):
            with patch('sys.argv', ['monitor_cluster.py', '--database', 'test_db']):
                from monitor_cluster import main
                main()
        
        mock_monitor.check_database_replication.assert_called_once_with('test_db')
    
    def test_main_with_continuous_monitoring(self, capsys):
        """Test main function with continuous monitoring"""
        mock_monitor = Mock()
        
        with patch('monitor_cluster.CouchDBMonitor', return_value=mock_monitor):
            with patch('sys.argv', ['monitor_cluster.py', '--continuous', '--interval', '60']):
                from monitor_cluster import main
                main()
        
        mock_monitor.monitor_continuous.assert_called_once_with(60)
    
    def test_main_with_sync_success(self, capsys):
        """Test main function with database sync (success)"""
        mock_monitor = Mock()
        mock_monitor.sync_database.return_value = {"success": True, "results": {"node1": True}}
        
        with patch('monitor_cluster.CouchDBMonitor', return_value=mock_monitor):
            with patch('sys.argv', ['monitor_cluster.py', '--sync', 'test_db', '--wait']):
                from monitor_cluster import main
                main()
        
        mock_monitor.sync_database.assert_called_once_with('test_db', True)
        captured = capsys.readouterr()
        assert "✅ Sync initiated successfully" in captured.out
    
    def test_main_with_sync_failure(self, capsys):
        """Test main function with database sync (failure)"""
        mock_monitor = Mock()
        mock_monitor.sync_database.return_value = {"success": False, "error": "Sync failed"}
        
        with patch('monitor_cluster.CouchDBMonitor', return_value=mock_monitor):
            with patch('sys.argv', ['monitor_cluster.py', '--sync', 'test_db']):
                with patch('sys.exit') as mock_exit:
                    from monitor_cluster import main
                    main()
        
        mock_monitor.sync_database.assert_called_once_with('test_db', False)
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "❌ Sync failed" in captured.out
    
    def test_main_with_custom_backend_url(self, capsys):
        """Test main function with custom backend URL"""
        with patch('monitor_cluster.CouchDBMonitor') as mock_monitor_class:
            with patch('sys.argv', ['monitor_cluster.py', '--backend-url', 'http://custom:8000']):
                from monitor_cluster import main
                main()
        
        mock_monitor_class.assert_called_once_with('http://custom:8000')


class TestErrorHandling:
    """Test error handling in monitor"""
    
    @pytest.fixture
    def monitor(self):
        return CouchDBMonitor("http://localhost:5000")
    
    def test_handle_http_status_error(self, monitor):
        """Test handling of HTTP status errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_cluster_health()
            
            assert result["success"] is False
            assert "404 Not Found" in result["error"]
    
    def test_handle_connection_timeout(self, monitor):
        """Test handling of connection timeout"""
        with patch.object(monitor.session, 'get', side_effect=requests.Timeout("Request timeout")):
            result = monitor.get_cluster_health()
            
            assert result["success"] is False
            assert "Request timeout" in result["error"]
    
    def test_handle_json_decode_error(self, monitor):
        """Test handling of JSON decode errors"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with patch.object(monitor.session, 'get', return_value=mock_response):
            result = monitor.get_cluster_health()
            
            assert result["success"] is False
            assert "Invalid JSON" in result["error"]


@pytest.fixture(autouse=True)
def reset_sys_argv():
    """Reset sys.argv after each test"""
    import sys
    original_argv = sys.argv.copy()
    yield
    sys.argv = original_argv