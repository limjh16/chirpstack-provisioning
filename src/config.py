import os

def load_config():
    """Load configuration from environment variables."""
    return {
        'server': os.environ['CHIRPSTACK_SERVER'],
        'api_token': os.environ['CHIRPSTACK_API_KEY_TOKEN'],
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'idb_bucket1': os.environ['IDB_BUCKET_1'],
        'idb_bucket2': os.environ['IDB_BUCKET_2'],
        'idb_org': os.environ['IDB_ORG'],
        'idb_token': os.environ['IDB_TOKEN'],
        'idb_endpoint': os.environ['IDB_ENDPOINT']
    }