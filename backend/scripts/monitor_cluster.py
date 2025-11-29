#!/usr/bin/env python3
"""
CouchDB Cluster Monitoring Script
Monitors the health and replication status of the NoteBook CouchDB cluster
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional

class CouchDBMonitor:
    def __init__(self, backend_url: str = "http://localhost:5000"):
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        
    def get_cluster_health(self) -> Dict:
        """Get cluster health status"""
        try:
            response = self.session.get(f"{self.backend_url}/api/replication/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_replication_status(self, database: Optional[str] = None) -> Dict:
        """Get replication status"""
        try:
            url = f"{self.backend_url}/api/replication/status"
            if database:
                url += f"?database={database}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_app_health(self) -> Dict:
        """Get application health"""
        try:
            response = self.session.get(f"{self.backend_url}/api/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_replication_info(self) -> Dict:
        """Get replication configuration info"""
        try:
            response = self.session.get(f"{self.backend_url}/api/replication/info")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def sync_database(self, database: str, wait: bool = False) -> Dict:
        """Force database synchronization"""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/replication/sync",
                json={"database": database, "wait": wait}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def print_health_summary(self):
        """Print a comprehensive health summary"""
        print("=" * 60)
        print(f"CouchDB Cluster Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Application Health
        app_health = self.get_app_health()
        if app_health.get('status') == 'healthy':
            print("✅ Application: HEALTHY")
        else:
            print("❌ Application: UNHEALTHY")
            print(f"   Error: {app_health.get('error', 'Unknown')}")
        
        print()
        
        # Replication Configuration
        repl_info = self.get_replication_info()
        if repl_info.get('success'):
            info = repl_info['info']
            print("📋 Replication Configuration:")
            print(f"   Enabled: {'✅ YES' if info['replication_enabled'] else '❌ NO'}")
            print(f"   Primary URL: {info['primary_url']}")
            print(f"   Replica Nodes: {len(info['replication_nodes'])}")
            for i, node in enumerate(info['replication_nodes'], 1):
                print(f"     {i}. {node}")
            print(f"   Continuous: {'✅ YES' if info['continuous_replication'] else '❌ NO'}")
            print(f"   Retry Interval: {info['retry_seconds']}s")
        
        print()
        
        # Cluster Health
        cluster_health = self.get_cluster_health()
        if cluster_health.get('success'):
            print("🏥 Cluster Node Health:")
            nodes = cluster_health['nodes']
            healthy_count = 0
            for node_url, node_info in nodes.items():
                status = node_info['status']
                if status == 'healthy':
                    print(f"   ✅ {node_url} - v{node_info.get('version', 'unknown')}")
                    healthy_count += 1
                else:
                    print(f"   ❌ {node_url} - {node_info.get('error', 'unknown error')}")
            print(f"   Summary: {healthy_count}/{len(nodes)} nodes healthy")
        else:
            print(f"❌ Failed to get cluster health: {cluster_health.get('error')}")
        
        print()
        
        # Replication Status
        repl_status = self.get_replication_status()
        if repl_status.get('success'):
            replications = repl_status['replications']
            if replications:
                print("🔄 Active Replications:")
                active_count = 0
                error_count = 0
                
                for repl_id, repl_info in replications.items():
                    state = repl_info['state']
                    if state in ['running', 'completed']:
                        status_icon = "✅"
                        active_count += 1
                    elif state == 'error':
                        status_icon = "❌"
                        error_count += 1
                    else:
                        status_icon = "⚠️"
                    
                    print(f"   {status_icon} {repl_id}")
                    print(f"       State: {state}")
                    print(f"       Source: {repl_info['source']}")
                    print(f"       Target: {repl_info['target']}")
                    
                    if 'docs_read' in repl_info:
                        print(f"       Docs Read: {repl_info['docs_read']}")
                        print(f"       Docs Written: {repl_info['docs_written']}")
                        if repl_info.get('doc_write_failures', 0) > 0:
                            print(f"       ⚠️ Write Failures: {repl_info['doc_write_failures']}")
                
                print(f"   Summary: {active_count} active, {error_count} errors")
            else:
                print("🔄 No active replications found")
        else:
            print(f"❌ Failed to get replication status: {repl_status.get('error')}")
        
        print("=" * 60)
    
    def monitor_continuous(self, interval: int = 30):
        """Continuously monitor cluster health"""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                self.print_health_summary()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def check_database_replication(self, database: str):
        """Check replication status for a specific database"""
        print(f"Checking replication for database: {database}")
        print("-" * 50)
        
        repl_status = self.get_replication_status(database)
        if repl_status.get('success'):
            replications = repl_status['replications']
            if replications:
                for repl_id, repl_info in replications.items():
                    print(f"Replication: {repl_id}")
                    print(f"  State: {repl_info['state']}")
                    print(f"  Continuous: {repl_info['continuous']}")
                    print(f"  Last Updated: {repl_info['last_updated']}")
                    
                    if 'docs_read' in repl_info:
                        print(f"  Documents Read: {repl_info['docs_read']}")
                        print(f"  Documents Written: {repl_info['docs_written']}")
                        print(f"  Revisions Checked: {repl_info['revisions_checked']}")
                        
                        if repl_info.get('doc_write_failures', 0) > 0:
                            print(f"  ⚠️ Write Failures: {repl_info['doc_write_failures']}")
                    print()
            else:
                print(f"No replications found for database: {database}")
        else:
            print(f"Error: {repl_status.get('error')}")

def main():
    parser = argparse.ArgumentParser(description="CouchDB Cluster Monitor")
    parser.add_argument("--backend-url", default="http://localhost:5000", 
                       help="Backend API URL (default: http://localhost:5000)")
    parser.add_argument("--database", help="Check specific database replication")
    parser.add_argument("--continuous", action="store_true", 
                       help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=30,
                       help="Monitoring interval in seconds (default: 30)")
    parser.add_argument("--sync", help="Force sync for specified database")
    parser.add_argument("--wait", action="store_true",
                       help="Wait for sync completion (use with --sync)")
    
    args = parser.parse_args()
    
    monitor = CouchDBMonitor(args.backend_url)
    
    if args.sync:
        print(f"Forcing sync for database: {args.sync}")
        result = monitor.sync_database(args.sync, args.wait)
        if result.get('success'):
            print("✅ Sync initiated successfully")
            if args.wait:
                print("⏳ Waiting for completion...")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Sync failed: {result.get('error')}")
            sys.exit(1)
    
    elif args.database:
        monitor.check_database_replication(args.database)
    
    elif args.continuous:
        monitor.monitor_continuous(args.interval)
    
    else:
        monitor.print_health_summary()

if __name__ == "__main__":
    main()