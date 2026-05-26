from .base import *

DEBUG = True
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
LOGGING['root']['level'] = LOG_LEVEL
LOGGING['loggers'] = {
    'httpcore': {'level': 'WARNING'},
    'httpx': {'level': 'WARNING'},
    'urllib3': {'level': 'WARNING'},
    'chromadb': {'level': 'INFO'},
}
