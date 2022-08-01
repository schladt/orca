from hashlib import sha384
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy import Index, Computed

Base = declarative_base()

# association table for artifact and tags MtM relationship
artifact_tags = Table('artifacts_tags', Base.metadata,
    Column('artifact_id', ForeignKey('artifacts.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

Index('artifacts_tags_idx_artifact_id', artifact_tags.c.artifact_id)
Index('artifacts_tags_idx_tag_id', artifact_tags.c.tag_id)

class TSVector(TypeDecorator):
    """
    Class to utilize postgres tsvectors in full text search
    """
    impl = TSVECTOR
    


class Artifact(Base) : 
    """
    Artifact table object
    """
    __tablename__ = 'artifacts'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    md5 = Column(String(32), unique=True)
    sha1 = Column(String(40), unique=True)
    sha256 = Column(String(64), unique=True)
    sha512 = Column(String(128), unique=True)
    sha384 = Column(String(96), unique=True)

    # MtM relationship with tags
    tags = relationship('Tag', secondary=artifact_tags, back_populates='artifacts')

    def __init__(self, md5=None, sha1=None, sha256=None, sha512=None):
        self.md5 = md5
        self.sha1 = sha1
        self.sha256 = sha256
        self.sha512 = sha512

class Tag(Base):
    """
    Tag table object
    """
    __tablename__ = 'tags'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    type = Column(String(128), unique=False)
    value = Column(Text, unique=False)

    # MtM relationship with artifacts
    artifacts = relationship('Artifact', secondary=artifact_tags, back_populates='tags')

    # use tsvectors 
    # see https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
    __ts_vector__ = Column(TSVector(),Computed("to_tsvector('english', type || ' ' || value)", persisted=True))

    # tables args used to create  ts_vector index and composite unique constraints
    __table_args__ = (
        Index('ix_tag___ts_vector__', __ts_vector__, postgresql_using='gin'),
        UniqueConstraint('type', 'value'),
    )


    def __init__(self, type, value):
        self.type = type
        self.value = value

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
