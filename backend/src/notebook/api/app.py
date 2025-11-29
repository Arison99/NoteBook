# Entry point for NoteBook backend
from flask import Flask, request, jsonify
from flask_cors import CORS
from ariadne import graphql_sync, make_executable_schema
import os
import logging
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import from new package structure
from ..core.schema import type_defs, query, mutation
from ..database.couchdb_client import replication_manager, get_replication_status, check_cluster_health, sync_database, setup_replication

# Import config using sys.path manipulation for now
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Create GraphQL schema
    schema = make_executable_schema(type_defs, [query, mutation])
    
    # Register routes
    register_graphql_routes(app, schema)
    register_api_routes(app)
    
    return app

def register_graphql_routes(app, schema):
    """Register GraphQL routes"""
    
    @app.route("/graphql", methods=["POST"])
    def graphql_server():
        data = request.get_json()
        success, result = graphql_sync(
            schema,
            data,
            debug=app.config['DEBUG']
        )
        status_code = 200 if success else 400
        return jsonify(result), status_code

def register_api_routes(app):
    """Register REST API routes"""
    
    # Replication Management Endpoints
    @app.route("/api/replication/status", methods=["GET"])
    def replication_status():
        """Get status of all replications"""
        try:
            db_name = request.args.get('database')
            status = get_replication_status(db_name)
            return jsonify({
                'success': True,
                'replications': status,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to get replication status: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route("/api/replication/health", methods=["GET"])
    def cluster_health():
        """Check health of all cluster nodes"""
        try:
            health = check_cluster_health()
            return jsonify({
                'success': True,
                'nodes': health,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to check cluster health: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route("/api/replication/sync", methods=["POST"])
    def sync_database_endpoint():
        """Force sync of a database"""
        try:
            data = request.get_json()
            db_name = data.get('database')
            wait_for_completion = data.get('wait', False)
            
            if not db_name:
                return jsonify({
                    'success': False,
                    'error': 'Database name is required'
                }), 400
            
            results = sync_database(db_name, wait_for_completion)
            return jsonify({
                'success': True,
                'database': db_name,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to sync database: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route("/api/replication/setup", methods=["POST"])
    def setup_database_replication():
        """Setup replication for a database"""
        try:
            data = request.get_json()
            db_name = data.get('database')
            bidirectional = data.get('bidirectional', True)
            
            if not db_name:
                return jsonify({
                    'success': False,
                    'error': 'Database name is required'
                }), 400
            
            results = setup_replication(db_name, bidirectional)
            return jsonify({
                'success': True,
                'database': db_name,
                'bidirectional': bidirectional,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to setup replication: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route("/api/replication/info", methods=["GET"])
    def replication_info():
        """Get general replication configuration info"""
        try:
            info = {
                'replication_enabled': replication_manager is not None,
                'primary_url': os.environ.get('COUCHDB_URL', 'http://localhost:5984/'),
                'replication_nodes': os.environ.get('REPLICATION_NODES', '').split(',') if os.environ.get('REPLICATION_NODES') else [],
                'continuous_replication': os.environ.get('CONTINUOUS_REPLICATION', 'true').lower() == 'true',
                'retry_seconds': int(os.environ.get('REPLICATION_RETRY_SECONDS', '30')),
                'timestamp': datetime.utcnow().isoformat()
            }
            return jsonify({
                'success': True,
                'info': info
            })
        except Exception as e:
            logger.error(f"Failed to get replication info: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route("/api/health", methods=["GET"])
    def app_health():
        """Application health check"""
        try:
            health_info = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'replication_enabled': replication_manager is not None,
                'database_cluster': check_cluster_health() if replication_manager else {'single_node': True}
            }
            return jsonify(health_info)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

# Legacy support - create app instance for backwards compatibility
app = create_app()

def initialize_replication():
    """Initialize replication on app startup"""
    logger.info("Starting NoteBook backend with distributed replication support")
    
    if replication_manager:
        logger.info(f"Replication enabled with {len(replication_manager.nodes)} nodes")
        
        # Setup replication for core databases on startup
        core_databases = ['pdfs', 'categories', 'analytics']
        for db_name in core_databases:
            try:
                setup_replication(db_name)
                logger.info(f"Replication setup completed for database: {db_name}")
            except Exception as e:
                logger.error(f"Failed to setup replication for {db_name}: {e}")
    else:
        logger.info("Running in single-node mode (no replication nodes configured)")

# Initialize replication when module is imported
initialize_replication()
