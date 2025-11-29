import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
import docker
import subprocess
from pathlib import Path


class TestDockerCompose:
    """Test Docker Compose configuration and deployment"""
    
    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml file exists and is valid"""
        compose_file = Path("docker-compose.yml")
        assert compose_file.exists(), "docker-compose.yml file should exist"
        
        # Try to parse it as YAML (basic validation)
        import yaml
        with open(compose_file, 'r') as f:
            try:
                compose_config = yaml.safe_load(f)
                assert 'services' in compose_config
                assert 'networks' in compose_config
                assert 'volumes' in compose_config
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in docker-compose.yml: {e}")
    
    def test_required_services_present(self):
        """Test that all required services are present in docker-compose"""
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        required_services = [
            'couchdb-primary',
            'couchdb-replica1', 
            'couchdb-replica2',
            'notebook-backend'
        ]
        
        services = compose_config.get('services', {})
        for service in required_services:
            assert service in services, f"Service {service} should be present in docker-compose.yml"
    
    def test_couchdb_environment_variables(self):
        """Test CouchDB services have correct environment variables"""
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        couchdb_services = ['couchdb-primary', 'couchdb-replica1', 'couchdb-replica2']
        services = compose_config.get('services', {})
        
        for service_name in couchdb_services:
            service = services[service_name]
            env = service.get('environment', {})
            
            # Check required environment variables
            assert 'COUCHDB_USER' in env
            assert 'COUCHDB_PASSWORD' in env
            assert 'COUCHDB_SECRET' in env
            assert 'NODENAME' in env
            
            # Check values
            assert env['COUCHDB_USER'] == 'Admin'
            assert env['COUCHDB_PASSWORD'] == 'password123'
    
    def test_backend_environment_variables(self):
        """Test backend service has correct environment variables"""
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        backend_service = compose_config['services']['notebook-backend']
        env = backend_service.get('environment', {})
        
        # Check required environment variables
        assert 'COUCHDB_URL' in env
        assert 'REPLICATION_NODES' in env
        assert 'CONTINUOUS_REPLICATION' in env
        
        # Check values
        assert env['COUCHDB_URL'] == 'http://couchdb-primary:5984/'
        assert 'couchdb-replica1' in env['REPLICATION_NODES']
        assert 'couchdb-replica2' in env['REPLICATION_NODES']
    
    def test_port_mappings(self):
        """Test that services have correct port mappings"""
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        services = compose_config.get('services', {})
        
        # Check port mappings
        expected_ports = {
            'couchdb-primary': ['5984:5984'],
            'couchdb-replica1': ['5985:5984'],
            'couchdb-replica2': ['5986:5984'],
            'notebook-backend': ['5000:5000']
        }
        
        for service_name, expected in expected_ports.items():
            if service_name in services:
                ports = services[service_name].get('ports', [])
                for expected_port in expected:
                    assert expected_port in ports, f"Service {service_name} should have port mapping {expected_port}"


class TestDockerfile:
    """Test Dockerfile configuration"""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile = Path("Dockerfile")
        assert dockerfile.exists(), "Dockerfile should exist"
    
    def test_dockerfile_has_required_instructions(self):
        """Test that Dockerfile has required instructions"""
        with open("Dockerfile", 'r') as f:
            dockerfile_content = f.read()
        
        required_instructions = [
            'FROM python:',
            'WORKDIR /app',
            'COPY requirements.txt',
            'RUN pip install',
            'COPY . .',
            'EXPOSE 5000',
            'HEALTHCHECK',
            'CMD ["python", "app.py"]'
        ]
        
        for instruction in required_instructions:
            assert instruction in dockerfile_content, f"Dockerfile should contain: {instruction}"
    
    def test_dockerfile_security_practices(self):
        """Test that Dockerfile follows security best practices"""
        with open("Dockerfile", 'r') as f:
            dockerfile_content = f.read()
        
        # Check for non-root user
        assert 'groupadd' in dockerfile_content or 'adduser' in dockerfile_content
        assert 'USER' in dockerfile_content
        
        # Check for proper file permissions
        assert 'chown' in dockerfile_content


class TestHAProxyConfiguration:
    """Test HAProxy configuration"""
    
    def test_haproxy_config_exists(self):
        """Test that HAProxy configuration exists"""
        haproxy_config = Path("haproxy.cfg")
        assert haproxy_config.exists(), "haproxy.cfg should exist"
    
    def test_haproxy_config_has_required_sections(self):
        """Test that HAProxy config has required sections"""
        with open("haproxy.cfg", 'r') as f:
            config_content = f.read()
        
        required_sections = [
            'global',
            'defaults',
            'frontend couchdb_frontend',
            'backend couchdb_servers',
            'stats enable'
        ]
        
        for section in required_sections:
            assert section in config_content, f"HAProxy config should contain section: {section}"
    
    def test_haproxy_backend_servers(self):
        """Test that HAProxy backend has all CouchDB servers"""
        with open("haproxy.cfg", 'r') as f:
            config_content = f.read()
        
        expected_servers = [
            'server couchdb-primary couchdb-primary:5984',
            'server couchdb-replica1 couchdb-replica1:5984',
            'server couchdb-replica2 couchdb-replica2:5984'
        ]
        
        for server in expected_servers:
            assert server in config_content, f"HAProxy config should contain: {server}"


class TestEnvironmentConfiguration:
    """Test environment configuration"""
    
    def test_env_example_exists(self):
        """Test that .env.example file exists"""
        env_example = Path(".env.example")
        assert env_example.exists(), ".env.example should exist"
    
    def test_env_example_has_required_variables(self):
        """Test that .env.example has all required variables"""
        with open(".env.example", 'r') as f:
            env_content = f.read()
        
        required_vars = [
            'COUCHDB_URL',
            'COUCHDB_USER', 
            'COUCHDB_PASSWORD',
            'REPLICATION_NODES',
            'CONTINUOUS_REPLICATION',
            'REPLICATION_RETRY_SECONDS'
        ]
        
        for var in required_vars:
            assert var in env_content, f".env.example should contain variable: {var}"
    
    def test_env_example_has_examples(self):
        """Test that .env.example provides usage examples"""
        with open(".env.example", 'r') as f:
            env_content = f.read()
        
        # Should have commented examples
        assert "# Example" in env_content
        assert "localhost:5984" in env_content
        assert "localhost:5985" in env_content


class TestIntegrationSetup:
    """Integration tests for the complete setup"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"), 
                       reason="Integration tests require RUN_INTEGRATION_TESTS=1")
    def test_docker_compose_syntax_validation(self):
        """Test Docker Compose syntax validation"""
        try:
            result = subprocess.run(
                ["docker-compose", "config"],
                capture_output=True,
                text=True,
                check=True
            )
            # If we get here, the syntax is valid
            assert "services:" in result.stdout
        except subprocess.CalledProcessError as e:
            pytest.fail(f"docker-compose config failed: {e.stderr}")
        except FileNotFoundError:
            pytest.skip("docker-compose not available")
    
    @pytest.mark.integration  
    @pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"),
                       reason="Integration tests require RUN_INTEGRATION_TESTS=1")
    def test_dockerfile_build_validation(self):
        """Test that Dockerfile can be built successfully"""
        try:
            # Create a temporary build context
            import tempfile
            import shutil
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy necessary files to temp directory
                files_to_copy = [
                    "Dockerfile",
                    "requirements.txt", 
                    "app.py",
                    "couchdb_client.py",
                    "schema.py"
                ]
                
                for file_name in files_to_copy:
                    if os.path.exists(file_name):
                        shutil.copy2(file_name, temp_dir)
                
                # Try to build the Docker image
                result = subprocess.run([
                    "docker", "build", 
                    "-t", "notebook-backend-test",
                    temp_dir
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    pytest.fail(f"Docker build failed: {result.stderr}")
                
                # Clean up test image
                subprocess.run(["docker", "rmi", "notebook-backend-test"], 
                             capture_output=True)
                
        except FileNotFoundError:
            pytest.skip("Docker not available")


class TestDeploymentValidation:
    """Test deployment configuration validation"""
    
    def test_required_files_present(self):
        """Test that all required deployment files are present"""
        required_files = [
            "docker-compose.yml",
            "Dockerfile",
            "haproxy.cfg",
            ".env.example",
            "requirements.txt",
            "REPLICATION_GUIDE.md"
        ]
        
        for file_name in required_files:
            file_path = Path(file_name)
            assert file_path.exists(), f"Required file {file_name} should exist"
    
    def test_requirements_has_all_dependencies(self):
        """Test that requirements.txt has all necessary dependencies"""
        with open("requirements.txt", 'r') as f:
            requirements_content = f.read()
        
        required_packages = [
            'flask',
            'couchdb',
            'python-dotenv',
            'ariadne',
            'pytest',
            'pytest-cov'
        ]
        
        for package in required_packages:
            assert package in requirements_content, f"requirements.txt should contain: {package}"
    
    def test_guide_documentation_completeness(self):
        """Test that the replication guide is comprehensive"""
        with open("REPLICATION_GUIDE.md", 'r') as f:
            guide_content = f.read()
        
        required_sections = [
            "## Overview",
            "## Features", 
            "## Quick Start",
            "## Configuration",
            "## API Endpoints",
            "## Troubleshooting",
            "## Security"
        ]
        
        for section in required_sections:
            assert section in guide_content, f"Guide should contain section: {section}"
    
    def test_monitoring_script_executable(self):
        """Test that monitoring script has proper structure"""
        monitor_script = Path("monitor_cluster.py")
        assert monitor_script.exists(), "monitor_cluster.py should exist"
        
        with open("monitor_cluster.py", 'r') as f:
            script_content = f.read()
        
        # Check for main components
        required_elements = [
            "class CouchDBMonitor",
            "def main():",
            "if __name__ == \"__main__\":",
            "argparse"
        ]
        
        for element in required_elements:
            assert element in script_content, f"Monitor script should contain: {element}"


class TestConfigurationConsistency:
    """Test consistency across configuration files"""
    
    def test_port_consistency(self):
        """Test that ports are consistent across all configuration files"""
        # Check docker-compose ports
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check HAProxy configuration
        with open("haproxy.cfg", 'r') as f:
            haproxy_content = f.read()
        
        # Verify CouchDB ports are consistent
        primary_port = "5984:5984"
        replica1_port = "5985:5984" 
        replica2_port = "5986:5984"
        
        # Check in docker-compose
        services = compose_config['services']
        assert primary_port in services['couchdb-primary']['ports']
        assert replica1_port in services['couchdb-replica1']['ports']
        assert replica2_port in services['couchdb-replica2']['ports']
        
        # Check HAProxy references the internal ports
        assert "couchdb-primary:5984" in haproxy_content
        assert "couchdb-replica1:5984" in haproxy_content
        assert "couchdb-replica2:5984" in haproxy_content
    
    def test_credential_consistency(self):
        """Test that credentials are consistent across configuration"""
        import yaml
        with open("docker-compose.yml", 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check that all CouchDB services use the same credentials
        couchdb_services = ['couchdb-primary', 'couchdb-replica1', 'couchdb-replica2']
        services = compose_config['services']
        
        expected_user = 'Admin'
        expected_password = 'password123'
        
        for service_name in couchdb_services:
            env = services[service_name]['environment']
            assert env['COUCHDB_USER'] == expected_user
            assert env['COUCHDB_PASSWORD'] == expected_password
        
        # Check backend service uses same credentials
        backend_env = services['notebook-backend']['environment']
        assert backend_env['COUCHDB_USER'] == expected_user
        assert backend_env['COUCHDB_PASSWORD'] == expected_password


# Test fixtures and utilities
@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for testing"""
    with patch('docker.from_env') as mock_docker:
        client = Mock()
        mock_docker.return_value = client
        yield client