# Domain models for DDD
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class PDF:
    id: str
    filename: str
    category: str
    encrypted_data: str  # Base64 encoded
    compressed: bool
    original_size_bytes: int
    compressed_size_bytes: int
    created_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int = 0

@dataclass
class Category:
    id: str
    name: str
    pdf_ids: List[str]
    created_at: datetime
    last_modified: datetime

@dataclass
class ActivityLog:
    id: str
    action: str  # 'upload', 'view', 'download', 'create_category', etc.
    resource_id: str
    resource_type: str  # 'pdf', 'category'
    timestamp: datetime
    metadata: dict = None
