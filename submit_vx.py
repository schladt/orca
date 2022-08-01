#Script to submit VX Underground files to CAPE

# create session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import os
import json
import time
import magic

from app.mappings_old import Artifact

engine = create_engine('sqlite:///db.sql', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

while 1:
    try:
        # check status of submitted tasks
        running_tasks = session.query(Artifact).filter_by(analysis_status=1).all()

        # check to see if any running tasks have completed
        for task in running_tasks:
            response = requests.get(f'http://127.0.0.1:8000/apiv2/tasks/status/{task.task_id}/')
            response = json.loads(response.text)
            if response['error'] != False:
                print(f'Changing status of {task.task_id} to FAILED')
                task.analysis_status = 2
            elif response['data'] == 'reported':
                print(f'Changing status of {task.task_id} to COMPLETE')
                task.analysis_status = 3
            elif response['data'] not in ['running', 'reported', 'completed', 'pending', 'distributed']:
                print(f'Changing status of {task.task_id} to FAILED')
                task.analysis_status = 2

        session.commit()


        # check if cape is ready for a new sample
        cape_status = requests.get('http://127.0.0.1:8000/apiv2/cuckoo/status/')
        cape_status = json.loads(cape_status.text)

        # only run if there are 3 machines available
        if cape_status['data']['machines']['available'] > 2:

            # get name and path of un-submitted sample
            sample = session.query(Artifact).filter_by(analysis_status=0).first()
            sample_path = os.path.join('/', 'home', 'cape', 'danger', sample.sha256)

            # check if file type is PE32
            filetype = magic.from_file(sample_path)
            if 'pe32' not in filetype.lower():
                print(f'Skipping {sample_path} with type {filetype}')
                sample.analysis_status = 2
                session.commit()
                continue

            # submit sample to cape
            print(f'Submitting sample {sample_path}')
            files = {'file': open(sample_path, 'rb')}
            response = requests.post('http://127.0.0.1:8000/apiv2/tasks/create/file/', files=files)

            # check for success
            if response.status_code != 200 or 'data' not in response.text:
                raise Exception(f'Received error while submitting {sample_path}: {response.text}')

            # update status and task id of artifact object
            response = json.loads(response.text)
            print(response['data']['message']) # DEBUG
            task_id = response['data']['task_ids'][0] 

            sample.analysis_status = 1
            sample.task_id = task_id

            session.commit()

        # wait XX seconds before submitting another sample
        time.sleep(15)
    except Exception as e:
        # brute force baby - set to error and try again
        print(f'Exception: {e}\nTrying next sample...')
        sample = session.query(Artifact).filter_by(analysis_status=0).first()
        sample.analysis_status = 2
        session.commit()
        time.sleep(15)
