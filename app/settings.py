"""
ORCA Settings File
These variables can be assigned dynamically (retrieved from a secrets vault) or statically set
"""
import logging

CAPE_URL = '127.0.0.1'
CAPE_PORT = 8000
DB_CONN_STRING = 'postgresql://postgres:postgres@localhost:5432/orca'
LOG_LEVEL = logging.DEBUG
JUPYTER_SERVER = 'http://127.0.0.1:8888/'