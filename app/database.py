
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import current_app, g, _app_ctx_stack

from app.settings import DB_CONN_STRING

def get_db_session():
    if 'db_session' not in g:
        engine = create_engine(DB_CONN_STRING)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        g.db_session = scoped_session(SessionLocal) 
    return g.db_session

def close_db_session(e=None):
    db = g.pop('db_session', None)

    if db is not None:
        db.close()

def get_db_connection():
    if 'db_connection' not in g:
        engine = create_engine(DB_CONN_STRING)
        g.db_connection = engine.raw_connection()
        return g.db_connection

def close_db_session(e=None):
    db_connection = g.pop('db_connection', None)
    if db_connection is not None:
        db_connection.close()
