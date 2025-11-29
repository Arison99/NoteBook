import couchdb
import os
import json
import logging
import time
from typing import List, Dict, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Primary CouchDB configuration
COUCHDB_URL = os.environ.get('COUCHDB_URL', 'http://localhost:5984/')
COUCHDB_USER = os.environ.get('COUCHDB_USER', 'Admin')
COUCHDB_PASSWORD = os.environ.get('COUCHDB_PASSWORD', 'password123')

# Replication nodes configuration
REPLICATION_NODES = os.environ.get('REPLICATION_NODES', '').split(',') if os.environ.get('REPLICATION_NODES') else []
REPLICATION_USER = os.environ.get('REPLICATION_USER', COUCHDB_USER)
REPLICATION_PASSWORD = os.environ.get('REPLICATION_PASSWORD', COUCHDB_PASSWORD)

# Replication settings
CONTINUOUS_REPLICATION = os.environ.get('CONTINUOUS_REPLICATION', 'true').lower() == 'true'
REPLICATION_FILTER = os.environ.get('REPLICATION_FILTER', '')
REPLICATION_RETRY_SECONDS = int(os.environ.get('REPLICATION_RETRY_SECONDS', '30'))

class CouchDBReplicationManager:
    """Manages distributed replication across multiple CouchDB nodes"""
    
    def __init__(self, primary_url: str, nodes: List[str], user: str, password: str):
        self.primary_url = primary_url
        self.nodes = [node.strip() for node in nodes if node.strip()]
        self.user = user
        self.password = password
        self.credentials = (user, password)
        
        # Initialize primary server
        self.primary_server = couchdb.Server(primary_url)
        self.primary_server.resource.credentials = self.credentials
        
        # Initialize replication servers
        self.replication_servers = {}
        for node in self.nodes:
            try:
                server = couchdb.Server(node)
                server.resource.credentials = self.credentials
                # Test connection
                server.version()
                self.replication_servers[node] = server
                logger.info(f"Connected to replication node: {node}")
            except Exception as e:
                logger.error(f"Failed to connect to replication node {node}: {e}")
    
    def get_primary_db(self, db_name: str):
        """Get or create database on primary server"""
        if db_name in self.primary_server:
            return self.primary_server[db_name]
        else:
            return self.primary_server.create(db_name)
    
    def setup_database_replication(self, db_name: str, bidirectional: bool = True) -> Dict[str, bool]:
        """Setup replication for a specific database across all nodes"""
        results = {}
        
        # Ensure database exists on all nodes
        for node_url, server in self.replication_servers.items():
            try:
                if db_name not in server:
                    server.create(db_name)
                    logger.info(f"Created database '{db_name}' on node: {node_url}")
            except Exception as e:
                logger.error(f"Failed to create database '{db_name}' on {node_url}: {e}")
                results[node_url] = False
                continue
        
        # Setup replication from primary to all nodes
        for node_url in self.replication_servers.keys():
            try:
                # Primary -> Node replication
                self._create_replication(
                    source=f"{self.primary_url}{db_name}",
                    target=f"{node_url}{db_name}",
                    replication_id=f"primary_to_{node_url.replace('://', '_').replace('/', '_')}_{db_name}",
                    continuous=CONTINUOUS_REPLICATION
                )
                
                # Node -> Primary replication (if bidirectional)
                if bidirectional:
                    self._create_replication(
                        source=f"{node_url}{db_name}",
                        target=f"{self.primary_url}{db_name}",
                        replication_id=f"{node_url.replace('://', '_').replace('/', '_')}_to_primary_{db_name}",
                        continuous=CONTINUOUS_REPLICATION
                    )
                
                results[node_url] = True
                logger.info(f"Replication setup complete for '{db_name}' with node: {node_url}")
                
            except Exception as e:
                logger.error(f"Failed to setup replication for '{db_name}' with {node_url}: {e}")
                results[node_url] = False
        
        return results
    
    def _create_replication(self, source: str, target: str, replication_id: str, continuous: bool = True):
        """Create a replication document"""
        replication_doc = {
            "_id": replication_id,
            "source": {
                "url": source,
                "auth": {
                    "basic": {
                        "username": self.user,
                        "password": self.password
                    }
                }
            },
            "target": {
                "url": target,
                "auth": {
                    "basic": {
                        "username": self.user,
                        "password": self.password
                    }
                }
            },
            "continuous": continuous,
            "create_target": True,
            "retry": True
        }
        
        if REPLICATION_FILTER:
            replication_doc["filter"] = REPLICATION_FILTER
        
        # Add replication document to _replicator database
        try:
            replicator_db = self.get_or_create_db('_replicator')
            
            # Check if replication already exists
            try:
                existing_doc = replicator_db[replication_id]
                # Update existing replication
                replication_doc["_rev"] = existing_doc["_rev"]
                replicator_db[replication_id] = replication_doc
                logger.info(f"Updated replication: {replication_id}")
            except couchdb.ResourceNotFound:
                # Create new replication
                replicator_db[replication_id] = replication_doc
                logger.info(f"Created replication: {replication_id}")
                
        except Exception as e:
            logger.error(f"Failed to create replication {replication_id}: {e}")
            raise
    
    def get_replication_status(self, db_name: str = None) -> Dict[str, Dict]:
        """Get status of all replications or for a specific database"""
        try:
            replicator_db = self.primary_server['_replicator']
            status = {}
            
            for doc_id in replicator_db:
                if doc_id.startswith('_'):
                    continue
                    
                doc = replicator_db[doc_id]
                
                # Filter by database if specified
                if db_name and db_name not in doc_id:
                    continue
                
                status[doc_id] = {
                    'state': doc.get('_replication_state', 'unknown'),
                    'source': doc.get('source', {}).get('url', 'unknown'),
                    'target': doc.get('target', {}).get('url', 'unknown'),
                    'continuous': doc.get('continuous', False),
                    'last_updated': doc.get('_replication_state_time', 'unknown')
                }
                
                if '_replication_stats' in doc:
                    stats = doc['_replication_stats']
                    status[doc_id].update({
                        'docs_read': stats.get('docs_read', 0),
                        'docs_written': stats.get('docs_written', 0),
                        'doc_write_failures': stats.get('doc_write_failures', 0),
                        'revisions_checked': stats.get('revisions_checked', 0)
                    })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get replication status: {e}")
            return {}
    
    def stop_replication(self, replication_id: str) -> bool:
        """Stop a specific replication"""
        try:
            replicator_db = self.primary_server['_replicator']
            doc = replicator_db[replication_id]
            del replicator_db[doc.id]
            logger.info(f"Stopped replication: {replication_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop replication {replication_id}: {e}")
            return False
    
    def stop_all_replications(self, db_name: str = None) -> Dict[str, bool]:
        """Stop all replications or for a specific database"""
        results = {}
        status = self.get_replication_status(db_name)
        
        for replication_id in status.keys():
            results[replication_id] = self.stop_replication(replication_id)
        
        return results
    
    def check_node_health(self) -> Dict[str, Dict]:
        """Check health status of all nodes"""
        health_status = {}
        
        # Check primary server
        try:
            version = self.primary_server.version()
            health_status[self.primary_url] = {
                'status': 'healthy',
                'version': version,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            health_status[self.primary_url] = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Check replication servers
        for node_url, server in self.replication_servers.items():
            try:
                version = server.version()
                health_status[node_url] = {
                    'status': 'healthy',
                    'version': version,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_status[node_url] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return health_status
    
    def perform_failover(self, failed_node: str, db_name: str) -> bool:
        """Perform failover when a node fails"""
        try:
            logger.warning(f"Performing failover for failed node: {failed_node}")
            
            # Remove failed node from active replications
            replications = self.get_replication_status(db_name)
            for repl_id, repl_info in replications.items():
                if failed_node in repl_info['source'] or failed_node in repl_info['target']:
                    self.stop_replication(repl_id)
                    logger.info(f"Stopped replication involving failed node: {repl_id}")
            
            # Remove failed node from active servers
            if failed_node in self.replication_servers:
                del self.replication_servers[failed_node]
                logger.info(f"Removed failed node from active servers: {failed_node}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failover failed for node {failed_node}: {e}")
            return False
    
    def sync_database(self, db_name: str, wait_for_completion: bool = False) -> Dict[str, bool]:
        """Trigger immediate synchronization for a database"""
        results = {}
        
        for node_url in self.replication_servers.keys():
            try:
                # Create one-time replication
                sync_id = f"sync_{db_name}_{int(time.time())}"
                self._create_replication(
                    source=f"{self.primary_url}{db_name}",
                    target=f"{node_url}{db_name}",
                    replication_id=sync_id,
                    continuous=False
                )
                
                if wait_for_completion:
                    # Wait for replication to complete
                    while True:
                        status = self.get_replication_status()
                        if sync_id in status:
                            state = status[sync_id]['state']
                            if state in ['completed', 'error', 'failed']:
                                break
                        time.sleep(1)
                
                results[node_url] = True
                logger.info(f"Sync initiated for '{db_name}' with node: {node_url}")
                
            except Exception as e:
                logger.error(f"Failed to sync '{db_name}' with {node_url}: {e}")
                results[node_url] = False
        
        return results

# Initialize replication manager
replication_manager = CouchDBReplicationManager(
    primary_url=COUCHDB_URL,
    nodes=REPLICATION_NODES,
    user=COUCHDB_USER,
    password=COUCHDB_PASSWORD
) if REPLICATION_NODES else None

# Primary server (backward compatibility)
server = couchdb.Server(COUCHDB_URL)
server.resource.credentials = (COUCHDB_USER, COUCHDB_PASSWORD)

def get_or_create_db(db_name):
    """Get or create database with replication setup"""
    if replication_manager:
        db = replication_manager.get_primary_db(db_name)
        # Setup replication for new databases
        if db_name not in server:
            logger.info(f"Setting up replication for new database: {db_name}")
            replication_manager.setup_database_replication(db_name)
        return db
    else:
        # Fallback to single server mode
        if db_name in server:
            return server[db_name]
        else:
            return server.create(db_name)

# Replication management functions
def setup_replication(db_name: str, bidirectional: bool = True) -> Dict[str, bool]:
    """Setup replication for a database"""
    if not replication_manager:
        logger.warning("Replication not configured - no replication nodes specified")
        return {}
    return replication_manager.setup_database_replication(db_name, bidirectional)

def get_replication_status(db_name: str = None) -> Dict[str, Dict]:
    """Get replication status"""
    if not replication_manager:
        return {}
    return replication_manager.get_replication_status(db_name)

def sync_database(db_name: str, wait_for_completion: bool = False) -> Dict[str, bool]:
    """Force immediate sync of a database"""
    if not replication_manager:
        logger.warning("Replication not configured - cannot sync database")
        return {}
    return replication_manager.sync_database(db_name, wait_for_completion)

def check_cluster_health() -> Dict[str, Dict]:
    """Check health of all cluster nodes"""
    if not replication_manager:
        return {COUCHDB_URL: {'status': 'healthy', 'note': 'single node mode'}}
    return replication_manager.check_node_health()

def stop_replication(replication_id: str) -> bool:
    """Stop a specific replication"""
    if not replication_manager:
        return False
    return replication_manager.stop_replication(replication_id)
