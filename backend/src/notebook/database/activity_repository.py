# Activity logging repository
from ..core.domain import ActivityLog
from .couchdb_client import get_or_create_db
import uuid
from datetime import datetime

ACTIVITY_DB = 'activities'

class ActivityRepository:
    def __init__(self):
        self.db = get_or_create_db(ACTIVITY_DB)

    def log_activity(self, action: str, resource_id: str, resource_type: str, metadata: dict = None):
        """Log an activity"""
        activity = ActivityLog(
            id=str(uuid.uuid4()),
            action=action,
            resource_id=resource_id,
            resource_type=resource_type,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        doc = {
            'type': 'activity',
            'id': activity.id,
            'action': activity.action,
            'resource_id': activity.resource_id,
            'resource_type': activity.resource_type,
            'timestamp': activity.timestamp.isoformat(),
            'metadata': activity.metadata
        }
        
        self.db.save(doc)
        return activity

    def get_activities_by_type(self, resource_type: str, limit: int = 100):
        """Get activities by resource type"""
        results = []
        for doc_id in self.db:
            doc = self.db[doc_id]
            if doc.get('type') == 'activity' and doc.get('resource_type') == resource_type:
                results.append(doc)
                if len(results) >= limit:
                    break
        return results

    def get_activities_by_action(self, action: str, limit: int = 100):
        """Get activities by action type"""
        results = []
        for doc_id in self.db:
            doc = self.db[doc_id]
            if doc.get('type') == 'activity' and doc.get('action') == action:
                results.append(doc)
                if len(results) >= limit:
                    break
        return results

    def get_recent_activities(self, days: int = 7, limit: int = 100):
        """Get recent activities within specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        results = []
        
        for doc_id in self.db:
            doc = self.db[doc_id]
            if doc.get('type') == 'activity':
                activity_date = datetime.fromisoformat(doc.get('timestamp', '1970-01-01'))
                if activity_date >= cutoff_date:
                    results.append(doc)
                    if len(results) >= limit:
                        break
        
        # Sort by timestamp descending
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results
