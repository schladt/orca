# setup database and tables
from app.mappings_old import Artifact, Tag, create_tables
create_tables()


# create session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db.sql', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Extract vx-underground files
# Create artifact and tag entries

import os
import magic
from py7zr import SevenZipFile
import hashlib

# walk sample directory to find .7z files
sample_dir = os.path.join('/', 'home', 'cape', 'samples', 'vx-underground')
danger_dir = os.path.join('/', 'home', 'cape', 'danger')

print(sample_dir)
for root, dirs, files in os.walk(sample_dir):
    for name in files:
        filename=os.path.join(root, name)
        try:
            filetype = magic.from_file(filename)
            filesize = os.path.getsize(filename)
            if '7-zip' in filetype.lower() and filesize < 20000000:
                print(f'Found {filename} with type {filetype} and size {filesize}')
                
                # extract file
                with SevenZipFile(filename, mode='r', password='infected') as z:
                    z.extractall(path=danger_dir)

                # create artifact object
                new_file = os.path.join(danger_dir, filename.split('.7z')[0].split('/')[-1])
                with open(new_file, 'rb') as f:
                    bytes = f.read() # read entire file as bytes
                    sha256 = hashlib.sha256(bytes).hexdigest().lower()

                artifact = session.query(Artifact).filter_by(sha256=sha256).first()
                if not artifact:
                    artifact = Artifact(sha256=sha256)
                session.add(artifact)
                

                # create family tag
                family = filename.split(sample_dir)[1].split('/')[1].lower()
                # remove spaces and special characters
                family = ''.join(e for e in family if e.isalnum())
                tag = session.query(Tag).filter_by(type='family', value=family).first()
                if not tag:
                    tag = Tag(type='family', value=family)
                session.add(tag)

                # associate tag with artifact
                artifact.tags.append(tag)

                session.commit()

                




        except:
            print(f'Error processing file. Skipping {filename} ...')
            pass