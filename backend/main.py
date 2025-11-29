#!/usr/bin/env python3
"""
NoteBook Backend Application Entry Point
GraphQL Learning Project with Distributed Replication
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from notebook.api.app import create_app

def main():
    """Main application entry point"""
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting NoteBook Backend on {host}:{port}")
    if debug:
        print("🔧 Running in development mode")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()