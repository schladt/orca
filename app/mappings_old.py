from email.policy import default
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy import BigInteger, Integer, String, Text

Base = declarative_base()

# association table for artifact and tags MtM relationship
artifact_tags = Table('artifacts_tags', Base.metadata,
    Column('artifact_id', ForeignKey('artifacts.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

class Artifact(Base) : 
    """
    Artifact table object
    Analysis status codes: 0=unprocessed, 1=pending, 2=failed, 3=complete
    """
    __tablename__ = 'artifacts'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    task_id = Column(BigInteger().with_variant(Integer, "sqlite"), unique=False, default=0)  
    md5 = Column(String(32), unique=True)
    sha1 = Column(String(40), unique=True)
    sha256 = Column(String(64), unique=True)
    sha512 = Column(String(128), unique=True)
    analysis_status = Column(Integer, unique=False, default=0)

    # MtM relationship with tags
    tags = relationship('Tag', secondary=artifact_tags, back_populates='artifacts')

    def __init__(self, md5=None, sha1=None, sha256=None, sha512=None, analysis_status=0):
        self.md5 = md5
        self.sha1 = sha1
        self.sha256 = sha256
        self.sha512 = sha512
        analysis_status = analysis_status


class Tag(Base):
    """
    Tag table object
    """
    __tablename__ = 'tags'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    type = Column(String(128), unique=False)
    value = Column(Text, unique=False)
    __table_args__ = (UniqueConstraint('type', 'value'),)

    # MtM relationship with artifacts
    artifacts = relationship('Artifact', secondary=artifact_tags, back_populates='tags')

    def __init__(self, type, value):
        self.type = type
        self.value = value

def create_tables():
    """
    Utility function to create tables in the database
    """    
    from sqlalchemy import create_engine

    engine = create_engine('sqlite:///db.sql', echo=True)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    """
    Main function creates database and tables
    """

    create_tables()
