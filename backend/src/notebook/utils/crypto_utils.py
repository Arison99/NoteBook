# Encryption and compression utilities
from cryptography.fernet import Fernet
import zlib
import base64
import os
import json
from datetime import datetime

# Key management
KEY_STORE_FILE = 'key_store.json'
CURRENT_KEY_FILE = 'encryption.key'

def load_key_store():
    """Load the key store from file"""
    if os.path.exists(KEY_STORE_FILE):
        try:
            with open(KEY_STORE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_key_store(key_store):
    """Save the key store to file"""
    with open(KEY_STORE_FILE, 'w') as f:
        json.dump(key_store, f, indent=2)

def get_or_create_key():
    """Get existing key from file or create a new one"""
    key_store = load_key_store()
    
    # Try to load current key
    if os.path.exists(CURRENT_KEY_FILE):
        with open(CURRENT_KEY_FILE, 'rb') as f:
            current_key = f.read()
        
        # Store this key in our key store if not already there
        current_key_b64 = base64.b64encode(current_key).decode()
        if current_key_b64 not in key_store:
            key_store[current_key_b64] = {
                'created_at': datetime.now().isoformat(),
                'is_current': True
            }
            # Mark other keys as not current
            for key_id in key_store:
                if key_id != current_key_b64:
                    key_store[key_id]['is_current'] = False
            save_key_store(key_store)
        
        return current_key
    else:
        # Generate new key and save it
        key = Fernet.generate_key()
        with open(CURRENT_KEY_FILE, 'wb') as f:
            f.write(key)
        
        # Store in key store
        key_b64 = base64.b64encode(key).decode()
        key_store[key_b64] = {
            'created_at': datetime.now().isoformat(),
            'is_current': True
        }
        # Mark other keys as not current
        for key_id in key_store:
            if key_id != key_b64:
                key_store[key_id]['is_current'] = False
        save_key_store(key_store)
        
        print(f"Created new encryption key: {CURRENT_KEY_FILE}")
        return key

def get_all_keys():
    """Get all stored encryption keys"""
    key_store = load_key_store()
    keys = []
    for key_b64, info in key_store.items():
        try:
            key_bytes = base64.b64decode(key_b64.encode())
            keys.append((key_bytes, info))
        except:
            continue
    return keys

FERNET_KEY = get_or_create_key()
fernet = Fernet(FERNET_KEY)

def encrypt_data(data: bytes) -> bytes:
    """Encrypt data using the current key"""
    return fernet.encrypt(data)

def decrypt_data(token: bytes) -> bytes:
    """Decrypt data, trying multiple keys if necessary"""
    # First try with current key
    try:
        return fernet.decrypt(token)
    except Exception as e:
        print(f"Decryption failed with current key: {e}")
        
        # Try with all stored keys
        all_keys = get_all_keys()
        for key_bytes, key_info in all_keys:
            try:
                temp_fernet = Fernet(key_bytes)
                result = temp_fernet.decrypt(token)
                print(f"Successfully decrypted with key from {key_info.get('created_at', 'unknown date')}")
                return result
            except:
                continue
        
        # If all keys fail, raise the original exception
        raise Exception(f"Could not decrypt data with any available key. This usually means the data was encrypted with a different/missing key.")

def compress_data(data: bytes) -> bytes:
    return zlib.compress(data)

def decompress_data(data: bytes) -> bytes:
    return zlib.decompress(data)

def encode_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')

def decode_base64(data: str) -> bytes:
    return base64.b64decode(data.encode('utf-8'))
