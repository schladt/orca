"""
Mappings used to to manage CAPE analyses
"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy import Index, Computed

Base = declarative_base()

class CapeAnalysis(Base) : 
    """
    CAPE Analysis Object
    cape_id: cape task id
    artifact_id: orca Artifact primary key
    cape_status: cape analysis status codes: 0=unprocessed, 1=pending, 2=failed, 3=complete
    orca_status: orca tag generation status codes: 0=unprocessed, 1=pending, 2=failed, 3=complete
    """
    __tablename__ = 'cape_analyses'
    cape_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    artifact_id = Column(BigInteger().with_variant(Integer, "sqlite"), unique=False, default=0)  
    cape_status = Column(Integer, unique=False, default=0)
    orca_status = Column(Integer, unique=False, default=0)

    def __init__(self, cape_id=None, artifact_id=None, cape_status=None, orca_status=None):
        self.cape_id = cape_id
        self.artifact_id = artifact_id
        self.cape_status = cape_status
        self.orca_status = orca_status


def create_tables():
    """
    Utility function to create tables in the database
    """    
    from sqlalchemy import create_engine

    # engine = create_engine('sqlite:///db.sql', echo=True)
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/orca')
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    """
    Main function creates database and tables
    """

    create_tables()


