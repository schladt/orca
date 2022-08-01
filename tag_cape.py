"""
Utility script code for processing cape analyses to produce tags
"""
# code for processing cape analyses to produces tags

import time
import logging
import requests
import json 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.mappings_orca import Artifact, Tag
from app.mappings_cape import CapeAnalysis

from app.settings import DB_CONN_STRING
from app.settings import CAPE_URL
from app.settings import CAPE_PORT 
from app.settings import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s [%(levelname)s]: %(message)s')

# create sqlalchemy database session
engine = create_engine(DB_CONN_STRING)
Session = sessionmaker(bind=engine)
session = Session()

def store_tags(tags:list, artifact_id:int) -> int:
    """
    Stores given tags in database and creates artifact association if artifact id provided\n
    INPUT:\n
        tags (list of tuples): list of tag type, tag value pairs\n
        artifact_id (int):\n id of artifact to associated tags
    OUTPUT:\
        num_tag (int) - number of tags successfully stored in the database
    """

    # create primitive connection 
    connection = engine.raw_connection()
    cur = connection.cursor()

    # chunk tags for sql insert
    n=1000 
    # for i in range(8210, len(tags), n):
    for i in range(0, len(tags), n):
        # format tags as data string
        data_raw = tags[i:i+n]
        
        # remove duplicates
        data = []
        for x in data_raw:
            if x not in data:
                data.append(x)
        
        # create argument string
        args_str = b','.join(cur.mogrify("(%s,%s)", x) for x in data).decode('utf-8')
        stmt = f'INSERT INTO tags (type, value) VALUES {args_str} ON CONFLICT (type, value) DO UPDATE SET type=EXCLUDED.type RETURNING ID;'

        # insert tags\
        num_tags = 0
        try:
            cur.execute(stmt)
            results = cur.fetchall()
            num_tags = len(results)

            # create associations
            if artifact_id:

                data_str = ''
                for row in results:
                    data_str = f'{data_str},{artifact_id, row[0]}'
                data_str = data_str.strip(',')
                stmt = f'INSERT INTO artifacts_tags (artifact_id, tag_id) VALUES {data_str} ON CONFLICT DO NOTHING'
                # print(stmt)
                cur.execute(stmt)
                    
        except Exception as e:
            print(i)
            print(stmt)
            raise e
    
    
    connection.commit()
    cur.close()
    connection.close()

    return num_tags

def process_report(report, artifact_id=None):
    """
    Processes CAPE report to produce tags which are stored in the database and associated with given artifact id
    INPUT: report (dict) - CAPE report to process
    INPUT: artifact_id (int) - ID of artifact to associate newly created tags
    OUTPUT: tags_created (int) - Number of tags created 
    """
    tags = []

    # create behavior tags
    if 'behavior' in report:
        if 'processes' in report['behavior']:
            for process in report['behavior']['processes']:
                # create tag for process name
                tag_type = 'process_name'
                tag_value = process['process_name']
                tags.append((tag_type, tag_value))

                # create tag for each process call
                if 'calls' in process:
                    for call in process['calls']:
                        del(call['timestamp'])
                        del(call['thread_id'])
                        del(call['caller'])
                        del(call['parentcaller'])
                        if 'arguments' in call:
                            for arg in call['arguments']:
                                del(arg['value'])
                        if len(str(call)) > 1500:
                            del(call['arguments'])

                        report['behavior']['processes'][0]['calls'][0]

                        tag_type = 'process_call'
                        tag_value = json.dumps(call)
                        tags.append((tag_type, tag_value))
        
        # create tags from summary items
        if 'summary' in report['behavior']:
            # files
            if 'files' in report['behavior']['summary']:
                for file in report['behavior']['summary']['files']:
                    tag_type = 'file'
                    tag_value = file
                    tags.append((tag_type, tag_value))

            # read_file
            if 'read_files' in report['behavior']['summary']:
                for read_file in report['behavior']['summary']['read_files']:
                    tag_type = 'read_file'
                    tag_value = read_file
                    tags.append((tag_type, tag_value))

            # write_file
            if 'write_files' in report['behavior']['summary']:
                for write_file in report['behavior']['summary']['write_files']:
                    tag_type = 'write_file'
                    tag_value = write_file
                    tags.append((tag_type, tag_value))

            # delete_file
            if 'delete_files' in report['behavior']['summary']:
                for delete_file in report['behavior']['summary']['delete_files']:
                    tag_type = 'delete_file'
                    tag_value = delete_file
                    tags.append((tag_type, tag_value))

            # reg_key
            if 'keys' in report['behavior']['summary']:
                for reg_key in report['behavior']['summary']['keys']:
                    tag_type = 'reg_key'
                    tag_value = reg_key
                    tags.append((tag_type, tag_value))

            # read_key
            if 'read_keys' in report['behavior']['summary']:
                for read_key in report['behavior']['summary']['read_keys']:
                    tag_type = 'read_key'
                    tag_value = read_key
                    tags.append((tag_type, tag_value))

            # write_key
            if 'write_keys' in report['behavior']['summary']:
                for write_key in report['behavior']['summary']['write_keys']:
                    tag_type = 'write_key'
                    tag_value = write_key
                    tags.append((tag_type, tag_value))

            # delete_key
            if 'delete_keys' in report['behavior']['summary']:
                for delete_key in report['behavior']['summary']['delete_keys']:
                    tag_type = 'delete_key'
                    tag_value = delete_key
                    tags.append((tag_type, tag_value))

            # executed_command
            if 'executed_commands' in report['behavior']['summary']:
                for executed_command in report['behavior']['summary']['executed_commands']:
                    tag_type = 'executed_command'
                    tag_value = executed_command
                    tags.append((tag_type, tag_value))

            # resolved_api
            if 'resolved_apis' in report['behavior']['summary']:
                for resolved_api in report['behavior']['summary']['resolved_apis']:
                    tag_type = 'resolved_api'
                    tag_value = resolved_api
                    tags.append((tag_type, tag_value))

            # mutex
            if 'mutexes' in report['behavior']['summary']:
                for mutex in report['behavior']['summary']['mutexes']:
                    tag_type = 'mutex'
                    tag_value = mutex
                    tags.append((tag_type, tag_value))

            # created_service
            if 'created_services' in report['behavior']['summary']:
                for created_service in report['behavior']['summary']['created_services']:
                    tag_type = 'created_service'
                    tag_value = created_service
                    tags.append((tag_type, tag_value))

            # started_service
            if 'started_services' in report['behavior']['summary']:
                for started_service in report['behavior']['summary']['started_services']:
                    tag_type = 'started_service'
                    tag_value = started_service
                    tags.append((tag_type, tag_value))

    # create network tags
    if 'network' in report:
        if 'hosts' in report['network']:
            for host in report['network']['hosts']:
                tag_type = 'host_ip'
                tag_value = host['ip']
                tags.append((tag_type, tag_value))
                tag_type = 'host_country'
                tag_value = host['country_name']
                tags.append((tag_type, tag_value))

        if 'domains' in report['network']:
            for domain in report['network']['domains']:
                tag_type = 'domain'
                tag_value = domain['domain']
                tags.append((tag_type, tag_value))

        if 'tcp' in report['network']:
            for tcp in report['network']['tcp']:
                tag_type = 'tcp_src'
                tag_value = tcp['src']
                tags.append((tag_type, tag_value))
                tag_type = 'tcp_dst'
                tag_value = tcp['dst']
                tags.append((tag_type, tag_value))
                tag_type = 'tcp_sport'
                tag_value = tcp['sport']
                tags.append((tag_type, tag_value))
                tag_type = 'tcp_dport'
                tag_value = tcp['dport']
                tags.append((tag_type, tag_value))

        if 'udp' in report['network']:
            for udp in report['network']['udp']:
                tag_type = 'udp_src'
                tag_value = udp['src']
                tags.append((tag_type, tag_value))
                tag_type = 'udp_dst'
                tag_value = udp['dst']
                tags.append((tag_type, tag_value))
                tag_type = 'udp_sport'
                tag_value = udp['sport']
                tags.append((tag_type, tag_value))
                tag_type = 'udp_dport'
                tag_value = udp['dport']
                tags.append((tag_type, tag_value))


        if 'icmp' in report['network']:
            for icmp in report['network']['icmp']:
                tag_type = 'icmp'
                tag_value = str(icmp)
                tags.append((tag_type, tag_value))

        if 'http' in report['network']:
            for http in report['network']['http']:
                tag_type = 'http'
                tag_value = str(http)
                tags.append((tag_type, tag_value))

        if 'dns' in report['network']:
            for dns in report['network']['dns']:
                tag_type = 'dns_request'
                tag_value = dns['request']
                tags.append((tag_type, tag_value))
                tag_type = 'dns_type'
                tag_value = dns['type']
                tags.append((tag_type, tag_value))

    # create string tags
    if 'strings' in report:
        for string in report['strings']:
            if len(string) > 4:
                tag_type = 'string'
                tag_value = string[0:1000]
                tags.append((tag_type, tag_value))

    # create target tags
    if 'target' in report:
        if 'file' in report['target']:
            for k, v in report['target']['file'].items():
                if isinstance(v, str):
                    tag_type = k
                    tag_value = v
                    tags.append((tag_type, tag_value))
            
            # pe info
            if 'pe' in report['target']['file']:
                if 'imports' in report['target']['file']['pe']:
                    for k, v in report['target']['file']['pe']['imports'].items():
                        for imp in v['imports']:
                            tag_type = 'import'
                            imp_name = imp['name']
                            tag_value = f'{k}:{imp_name}'
                            tags.append((tag_type, tag_value))
                if 'exports' in report['target']['file']['pe']:
                    for export in report['target']['file']['pe']['exports']:
                        tag_type = 'export'
                        tag_value = str(export)
                        tags.append((tag_type, tag_value))
                if 'dirents' in report['target']['file']['pe']:
                    for dirent in report['target']['file']['pe']['dirents']:
                        tag_type = 'dirent'
                        tag_value = dirent['name']
                        tags.append((tag_type, tag_value))
                if 'resources' in report['target']['file']['pe']:
                    for resource in report['target']['file']['pe']['resources']:
                        tag_type = 'resource'
                        tag_value = resource['name']
                        tags.append((tag_type, tag_value))

    # create signature tags
    if 'signatures' in report:
        for signature in report['signatures']:
            tag_type = 'signature_name'
            tag_value = signature['name']
            tags.append((tag_type, tag_value))
            tag_type = 'signature_description'
            tag_value = signature['description']
            tags.append((tag_type, tag_value))

    # malscore tag
    if 'malscore' in report:
        tag_type = 'malscore'
        tag_value = report['malscore']
        tags.append((tag_type, tag_value))

    # skip large samples for now            
    if len(tags) > 100000:
        logging.warn(f'extracted {len(tags)} - over 100k threshold, skipping for now...')
        return 0

    logging.debug(f'extracted {len(tags)} - beginning tag creation and association')
    return store_tags(tags, artifact_id)

def get_report(id:int=None):
    """
    Retrieves the next unprocessed CAPE report
    INPUT: id (int, optional) CAPE analysis id to retrieve; if None, retrieve first unprocessed
    OUTPUT: report (dict) - report from CAPE (parsed from JSON to DICT)
    OUTPUT: analysis (CapeAnalysis) - object used for process orchestration - should be updated once processing completed
    """

    if id:
        analysis = session.query(CapeAnalysis).filter_by(cape_id=id).first()
    else:
        analysis = session.query(CapeAnalysis).filter_by(cape_status=3, orca_status=0).first()
    if not analysis:
        logging.warn('no CAPE reports ready to process')
        return None, None

    # get report via API 
    id = analysis.cape_id
    response = requests.get(f'http://{CAPE_URL}:{CAPE_PORT}/apiv2/tasks/get/report/{id}/json/')

    if response.status_code != 200:
        logging.error(f'received bad status from CAPE attempting to retrieve report: {response.text}')
        analysis.cape_status = 2
        session.commit()
        return None, analysis

    try:
        report = json.loads(response.text)
    except Exception as e:
        logging.error(f'unable to parse report: {e}')
        analysis.cape_status = 2
        session.commit()
        return None, analysis

    return report, analysis

if __name__ == '__main__': 
    while 1:

        # modified to get benign samples (tag_id 116)
        connection = engine.raw_connection()
        cur = connection.cursor()

        stmt = 'SELECT cape_id FROM cape_analyses JOIN artifacts_tags ON cape_analyses.artifact_id = artifacts_tags.artifact_id WHERE tag_id=116 AND cape_status=3 AND orca_status=0 LIMIT 1;'
        cur.execute(stmt)
        result = cur.fetchone()
        cape_id = result[0]



        report, analysis = get_report(cape_id)
        if not report or not analysis:
            time.sleep(10)
            continue
        analysis.orca_status=1
        session.commit()
        try:
            tags_created = process_report(report, analysis.artifact_id)
            if tags_created > 0:
                analysis.orca_status = 3
            else:
                analysis.orca_status = 2
        except Exception as e:
            logging.error(f'error creating tags for analysis {analysis.cape_id}: {e}')
            analysis.orca_status = 2

        session.commit()
