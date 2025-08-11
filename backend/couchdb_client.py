import couchdb
import os

COUCHDB_URL = os.environ.get('COUCHDB_URL', 'http://localhost:5984/')
COUCHDB_USER = os.environ.get('COUCHDB_USER', 'Admin')
COUCHDB_PASSWORD = os.environ.get('COUCHDB_PASSWORD', 'password123')

server = couchdb.Server(COUCHDB_URL)
server.resource.credentials = (COUCHDB_USER, COUCHDB_PASSWORD)

def get_or_create_db(db_name):
    if db_name in server:
        return server[db_name]
    else:
        return server.create(db_name)
