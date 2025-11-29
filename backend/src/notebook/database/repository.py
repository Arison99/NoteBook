# Repository for CouchDB access
from .couchdb_client import get_or_create_db
from ..core.domain import PDF, Category
from .activity_repository import ActivityRepository
from datetime import datetime
import uuid

PDF_DB = 'pdfs'
CATEGORY_DB = 'categories'

class PDFRepository:
    def __init__(self):
        self.db = get_or_create_db(PDF_DB)
        self.activity_repo = ActivityRepository()

    def add_pdf(self, pdf: PDF):
        doc = pdf.__dict__.copy()
        doc['_id'] = pdf.id
        # Convert datetime objects to ISO strings
        doc['created_at'] = pdf.created_at.isoformat()
        doc['last_accessed'] = pdf.last_accessed.isoformat() if pdf.last_accessed else None
        self.db.save(doc)
        
        # Log activity
        self.activity_repo.log_activity(
            action='upload',
            resource_id=pdf.id,
            resource_type='pdf',
            metadata={
                'filename': pdf.filename,
                'category': pdf.category,
                'original_size': pdf.original_size_bytes,
                'compressed': pdf.compressed
            }
        )

    def get_pdf(self, pdf_id: str):
        doc = self.db.get(pdf_id)
        if doc:
            # Update access tracking
            doc['access_count'] = doc.get('access_count', 0) + 1
            doc['last_accessed'] = datetime.now().isoformat()
            self.db.save(doc)
            
            # Log view activity
            self.activity_repo.log_activity(
                action='view',
                resource_id=pdf_id,
                resource_type='pdf',
                metadata={'filename': doc.get('filename')}
            )
            
            return dict(doc)
        return None

    def list_pdfs(self):
        return [dict(self.db[id]) for id in self.db]

    def get_storage_stats(self):
        """Get storage statistics for all PDFs"""
        total_original = 0
        total_compressed = 0
        compressed_count = 0
        total_count = 0
        
        for doc_id in self.db:
            doc = self.db[doc_id]
            total_count += 1
            total_original += doc.get('original_size_bytes', 0)
            total_compressed += doc.get('compressed_size_bytes', 0)
            if doc.get('compressed', False):
                compressed_count += 1
        
        return {
            'total_pdfs': total_count,
            'total_original_bytes': total_original,
            'total_compressed_bytes': total_compressed,
            'compressed_count': compressed_count,
            'compression_ratio': ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0
        }

class CategoryRepository:
    def __init__(self):
        self.db = get_or_create_db(CATEGORY_DB)
        self.activity_repo = ActivityRepository()

    def add_category(self, category: Category):
        doc = category.__dict__.copy()
        doc['_id'] = category.id
        # Convert datetime objects to ISO strings
        doc['created_at'] = category.created_at.isoformat()
        doc['last_modified'] = category.last_modified.isoformat()
        self.db.save(doc)
        
        # Log activity
        self.activity_repo.log_activity(
            action='create_category',
            resource_id=category.id,
            resource_type='category',
            metadata={'name': category.name}
        )

    def get_category(self, category_id: str):
        doc = self.db.get(category_id)
        return dict(doc) if doc else None

    def list_categories(self):
        return [dict(self.db[id]) for id in self.db]

    def update_category(self, category_id: str, **kwargs):
        """Update category with timestamp tracking"""
        doc = self.db.get(category_id)
        if doc:
            for key, value in kwargs.items():
                if key != '_id' and key != '_rev':
                    doc[key] = value
            doc['last_modified'] = datetime.now().isoformat()
            self.db.save(doc)
            
            # Log activity
            self.activity_repo.log_activity(
                action='update_category',
                resource_id=category_id,
                resource_type='category',
                metadata=kwargs
            )
            
            return dict(doc)
        return None
