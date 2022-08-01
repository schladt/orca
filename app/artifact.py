"""
Dashboard Blueprint for artifact view
"""

from random import seed
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from sqlalchemy import or_

from app.database import get_db_session, get_db_connection
from app.mappings_orca import Artifact, Tag, artifact_tags
from app.mappings_cape import CapeAnalysis

bp = Blueprint('artifact', __name__)


# artifact page
@bp.route('/artifact/<int:artifact_id>', methods=['GET'], strict_slashes=False)
@bp.route('/artifact', methods=['GET'], strict_slashes=False)
def artifact(artifact_id=None):
    
    # return template is no id
    if artifact_id is None: 
        return  render_template('artifact.html')

    # get session
    db_session = get_db_session()

    # get basic information on artifact
    results = db_session.query(Tag).join(artifact_tags, artifact_tags.c.tag_id==Tag.id).filter(artifact_tags.c.artifact_id==int(artifact_id),
            or_(Tag.type=='md5',
                Tag.type=='sha1',  
                Tag.type=='sha256',
                Tag.type=='sha3_384',
                Tag.type=='sha512',
                Tag.type=='name',
                Tag.type=='type',
                Tag.type=='disposition',
                Tag.type=='family',
                Tag.type=='signature_name'  
            )
        ).all()
    tags = [(x.type, x.value) for  x in results]
    artifact_info = {'id': artifact_id, 'tags': {}}

    for tag in tags:
        if tag[0] == 'family' or tag[0] == 'signature_name':
            if f'{tag[0]}' not in artifact_info['tags']:
                artifact_info['tags'][f'{tag[0]}'] = []
            artifact_info['tags'][f'{tag[0]}'].append(tag[1])
        else:
            artifact_info['tags'][f'{tag[0]}'] = tag[1]
        
    
    # get tags associated with artifact
    tags = db_session.query(Tag).join(artifact_tags, Tag.id == artifact_tags.c.tag_id).filter(artifact_tags.c.artifact_id==artifact_id).with_entities(Tag.id, Tag.type, Tag.value).all()


    # get tags associated with artifact
    tags_t = db_session.query(Tag).join(artifact_tags, Tag.id == artifact_tags.c.tag_id).filter(artifact_tags.c.artifact_id==artifact_id).with_entities(Tag.id, Tag.type, Tag.value).all()
    args = ", ".join([str(t[0]) for t in tags_t])

    # get artifacts counts for each associated tag
    stmt = f'SELECT tag_id, count(*) FROM artifacts_tags WHERE tag_id IN ({args}) GROUP BY (tag_id);'
    con = get_db_connection()
    cur = con.cursor()
    cur.execute(stmt)
    results = cur.fetchall()

    # combine counts with tags
    tags = []
    for idx in range(len(results)):
        tags.append((tags_t[idx][0], tags_t[idx][1], tags_t[idx][2], results[idx][1]))



    return render_template(
        'artifact.html',
        artifact_id = artifact_id,
        artifact_info = artifact_info,
        tags = tags
    )