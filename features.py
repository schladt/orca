"""
Functions to transform tags into features
"""

import json
import logging
from statistics import mean
from sklearn import feature_selection

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.mappings_orca import Artifact
from app.mappings_cape import CapeAnalysis
from app.settings import DB_CONN_STRING
from app.settings import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s [%(levelname)s]: %(message)s')

# create sqlalchemy database session
engine = create_engine(DB_CONN_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def create_features(artifact_id:int) -> dict:
    """
    Transforms tags associated with an artifact into features
    INPUT: artifact_id (int) - artifact to create features for
    OUTPUT: (dict) - python dictionary consisting of feature name and value key pairs
    """

    # get all tags for an artifact
    results = session.query(Artifact).filter_by(id=artifact_id).first()
    
    # return none if no artifact or tags
    if not results:
        return None
        
    tag_objs = results.tags
    if not tag_objs:
        return None
    
    
    # format tags to create a dict
    tags = {}
    for tag in tag_objs:
        if tag.type not in tags:
            tags[tag.type] = []
        tags[tag.type].append(tag.value)

    # create features
    features = {}

    # add, artifact id, family and disposition as labels and classese
    features['artifact_id'] = artifact_id

    if 'family' in tags:
        features['family'] = tags['family'][0]

    if 'disposition' in tags:
        features['disposition'] = tags['disposition'][0]

    # process call features
    # number of process calls
    if 'process_call' in tags:
        features['000'] = len(tags['process_call'])

        # process argument features
        arg_lengths = []
        for item in tags['process_call']:
            process_call = json.loads(item)
            if 'arguments' in process_call:
                arg_lengths.append(len(process_call['arguments']))
            else:
                arg_lengths.append(0)
        
        # max number of args for single call
        features['001'] = max(arg_lengths)

        # total number of args for all calls
        features['002'] = sum(arg_lengths)

        # mean number of args per call
        features['003'] = mean(arg_lengths)

    

    # TODO:
    # API count - requires separate feature for each API
    # Category count - requires separate feature for each category


    # summary features
    
    # get file length count, max, mean
    if 'file' in tags:
        file_lengths = []
        for item in tags['file']:
            file_lengths.append(len(item))
        features['004'] = len(file_lengths)
        features['005'] = max(file_lengths)
        features['006'] = mean(file_lengths)

    # get file reads, count, max, mean
    if 'read_file' in tags:
        file_reads = []
        for item in tags['read_file']:
            file_reads.append(len(item))
        features['007'] = len(file_reads)
        features['008'] = max(file_reads)
        features['009'] = mean(file_reads)

    # get file writes, count, max, mean
    if 'write_file' in tags:
        file_writes = []
        for item in tags['write_file']:
            file_writes.append(len(item))
        features['010'] = len(file_writes)
        features['011'] = max(file_writes)
        features['012'] = mean(file_writes)

    # get file deletes, count, max, mean
    if 'delete_file' in tags:
        delete_files = []
        for item in tags['delete_file']:
            delete_files.append(len(item))
        features['013'] = len(delete_files)
        features['014'] = max(delete_files)
        features['015'] = mean(delete_files)

    # get reg_key, count, max, mean
    if 'reg_key' in tags:
        reg_keys = []
        for item in tags['reg_key']:
            reg_keys.append(len(item))
        features['016'] = len(reg_keys)
        features['017'] = max(reg_keys)
        features['018'] = mean(reg_keys)

    # get read_key, count, max, mean
    if 'read_key' in tags:
        read_keys = []
        for item in tags['read_key']:
            read_keys.append(len(item))
        features['019'] = len(read_keys)
        features['020'] = max(read_keys)
        features['021'] = mean(read_keys)

    # get write_key, count, max, mean
    if 'write_key' in tags:
        write_keys = []
        for item in tags['write_key']:
            write_keys.append(len(item))
        features['022'] = len(write_keys)
        features['023'] = max(write_keys)
        features['024'] = mean(write_keys)

    # get delete_key, count, max, mean
    if 'delete_key' in tags:
        delete_keys = []
        for item in tags['delete_key']:
            delete_keys.append(len(item))
        features['025'] = len(delete_keys)
        features['026'] = max(delete_keys)
        features['027'] = mean(delete_keys)

    # get executed_command, count, max, mean
    if 'executed_command' in tags:
        executed_commands = []
        for item in tags['executed_command']:
            executed_commands.append(len(item))
        features['028'] = len(executed_commands)
        features['029'] = max(executed_commands)
        features['030'] = mean(executed_commands)

    # get resolved_api, count, max, mean
    if 'resolved_api' in tags:
        resolved_apis = []
        for item in tags['resolved_api']:
            resolved_apis.append(len(item))
        features['031'] = len(resolved_apis)
        features['032'] = max(resolved_apis)
        features['033'] = mean(resolved_apis)

    # get mutex, count, max, mean
    if 'mutex' in tags:
        mutexes = []
        for item in tags['mutex']:
            mutexes.append(len(item))
        features['034'] = len(mutexes)
        features['035'] = max(mutexes)
        features['036'] = mean(mutexes)

    # number of created services
    if 'created_service' in tags:
        features['037'] = len(tags['created_service'])
    
    # number of started services
    if 'created_service' in tags:
        features['038'] = len(tags['created_service'])

    # network features - these may be sparse
    # number of hosts
    if 'host_ip' in tags:
        features['039'] = len(tags['host_ip'])

    # get domain count, max, mean
    if 'domain' in tags:
        domains = []
        for item in tags['domain']:
            domains.append(len(item))
        features['040'] = len(domains)
        features['041'] = max(domains)
        features['042'] = mean(domains)
        
    # NOTE: These fields are too sparse
        # number of tcp
        # number of udp
        # number of icmp
        # number of dns
        # number of http

    # string features
    # get string count, max, mean
    if 'string' in tags:
        strings = []
        for item in tags['string']:
            strings.append(len(item))
        features['043'] = len(strings)
        features['044'] = max(strings)
        features['045'] = mean(strings)


    # target features
    # number of imports
    if 'import' in tags:
        imports = []
        for item in tags['import']:
            imports.append(len(item))
        features['046'] = len(imports)
        features['047'] = max(imports)
        features['048'] = mean(imports)
    
    # number of exports
    if 'export' in tags:
        exports = []
        for item in tags['export']:
            exports.append(len(item))
        features['049'] = len(exports)
        features['050'] = max(exports)
        features['051'] = mean(exports)

    # number of dirents
    if 'dirent' in tags:
        dirents = []
        for item in tags['dirent']:
            dirents.append(len(item))
        features['052'] = len(dirents)
        features['053'] = max(dirents)
        features['054'] = mean(dirents)

    # number of resources
    if 'resource' in tags:
        resources = []
        for item in tags['resource']:
            resources.append(len(item))
        features['052'] = len(resources)
        features['053'] = max(resources)
        features['054'] = mean(resources)

    # signature features
    # number of signature
    if 'signature_name' in tags:
        features['055'] = len(tags['signature_name'])

    return features

def get_all_features(fully_processed:bool=True, verbose=False) -> list:
    """
    Get features for all artifacts in the ORCA database 
    INPUT: fully_processed (bool) - only return artifacts for fully processed features
    INPUT: verbose (bool) - print a progress message every 100 artifacts
    OUTPUT: features - list of dicts
    """

    if fully_processed:
        artifact_ids = session.query(CapeAnalysis).filter_by(cape_status=3, orca_status=3).with_entities(CapeAnalysis.artifact_id).all()
    else:
        artifact_ids = session.query(Artifact).with_entities(Artifact.id).all()

    # remove nested tuple
    artifact_ids = [x[0] for x in artifact_ids]

    # get features
    feature_set = []
    i = 0
    for artifact_id in artifact_ids:
        features = create_features(artifact_id)
        if features:
            feature_set.append(features)
        if verbose and i % 10 == 0:
            logging.debug(f"... fetched {i} artifact's features")
        i += 1
     
    return feature_set
