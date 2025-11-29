# Service layer for PDF and Category logic
from ..core.domain import PDF, Category
from ..database.repository import PDFRepository, CategoryRepository
from ..utils.crypto_utils import encrypt_data, compress_data, encode_base64, decode_base64
from datetime import datetime
import uuid
import base64

class PDFService:
    def __init__(self):
        self.repo = PDFRepository()

    def create_pdf(self, filename, category, raw_data, should_compress=True):
        # Decode base64 to bytes
        pdf_bytes = base64.b64decode(raw_data)
        original_size = len(pdf_bytes)
        
        # Compress if requested
        if should_compress:
            pdf_bytes = compress_data(pdf_bytes)
        
        compressed_size = len(pdf_bytes)
        
        # Encrypt the data
        encrypted_bytes = encrypt_data(pdf_bytes)
        
        # Encode back to base64 for storage
        encrypted_data = encode_base64(encrypted_bytes)
        
        pdf = PDF(
            id=str(uuid.uuid4()), 
            filename=filename, 
            category=category, 
            encrypted_data=encrypted_data, 
            compressed=should_compress,
            original_size_bytes=original_size,
            compressed_size_bytes=compressed_size,
            created_at=datetime.now(),
            last_accessed=None,
            access_count=0
        )
        self.repo.add_pdf(pdf)
        return pdf

    def get_pdf(self, pdf_id):
        return self.repo.get_pdf(pdf_id)

    def get_pdf_data(self, pdf_id):
        """Get decrypted PDF data for viewing"""
        try:
            pdf = self.repo.get_pdf(pdf_id)
            if not pdf:
                return None
            
            # Decode from base64
            encrypted_bytes = decode_base64(pdf['encrypted_data'])
            
            # Decrypt the data
            from crypto_utils import decrypt_data, decompress_data
            try:
                decrypted_bytes = decrypt_data(encrypted_bytes)
            except Exception as e:
                print(f"Decryption failed for PDF {pdf_id}: {e}")
                print("This usually means the encryption key has changed since upload.")
                return None
            
            # Decompress if needed
            if pdf['compressed']:
                try:
                    decrypted_bytes = decompress_data(decrypted_bytes)
                except Exception as e:
                    print(f"Decompression failed for PDF {pdf_id}: {e}")
                    return None
            
            # Return as base64 for frontend
            return encode_base64(decrypted_bytes)
        except Exception as e:
            print(f"Error getting PDF data for {pdf_id}: {e}")
            return None

    def list_pdfs(self):
        return self.repo.list_pdfs()

class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    def create_category(self, name):
        category = Category(
            id=str(uuid.uuid4()), 
            name=name, 
            pdf_ids=[],
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        self.repo.add_category(category)
        return category

    def get_category(self, category_id):
        return self.repo.get_category(category_id)

    def list_categories(self):
        return self.repo.list_categories()
