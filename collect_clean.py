# setup database and tables
from app.mappings_old import Artifact, Tag, create_tables
create_tables()


# create session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db.sql', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Create artifact and tag entries

import os
import hashlib
import shutil

# walk sample directory to find files
sample_dir = os.path.join('/', 'home', 'cape', 'bin')
target_dir = os.path.join('/', 'home', 'cape', 'danger')

print(sample_dir)
for root, dirs, files in os.walk(sample_dir):
    for name in files:
        filename=os.path.join(root, name)

        ext = filename.split('.')[-1].lower()
        if ext == 'dll' or ext == 'exe':
            print(f'Found {filename} with type {ext}')
            
            # Get sh2256
            with open(filename, 'rb') as f:
                bytes = f.read() # read entire file as bytes
                sha256 = hashlib.sha256(bytes).hexdigest().lower()
            
            
            # copy file to hash
            new_file = os.path.join(target_dir, sha256)
            shutil.copyfile(filename, new_file)

            # create artifact object
            artifact = session.query(Artifact).filter_by(sha256=sha256).first()
            if not artifact:
                artifact = Artifact(sha256=sha256)
            session.add(artifact)
            

            # create disposition tag
            tag = session.query(Tag).filter_by(type='disposition', value='benign').first()
            if not tag:
                tag = Tag(type='disposition', value='benign')
            session.add(tag)

            # associate tag with artifact
            artifact.tags.append(tag)
            session.commit()

        # except:
        #     print(f'Error processing file. Skipping {filename} ...')
        #     pass
