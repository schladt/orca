"""
Dashboard Blueprint for ORCA Web App
"""

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from sqlalchemy import or_

from app.database import get_db_session, get_db_connection
from app.mappings_orca import Artifact, Tag, artifact_tags
from app.mappings_cape import CapeAnalysis

bp = Blueprint('dashboard', __name__)


# main dashboard page
@bp.route('/')
def index():
    # get both a raw connection and session
    db_connection = get_db_connection()
    db_session = get_db_session()

    # create cursor
    cur = db_connection.cursor()

    # get counts for artifacts and tags
    stmt = "SELECT n_live_tup FROM pg_stat_all_tables WHERE relname = 'tags';"
    cur.execute(stmt)
    num_tags = cur.fetchone()[0]

    # get counts for artifacts and tags
    stmt = "SELECT n_live_tup FROM pg_stat_all_tables WHERE relname = 'artifacts';"
    cur.execute(stmt)
    num_artifacts = cur.fetchone()[0]

    # get count of CAPE processed samples
    cape_processed = db_session.query(Artifact).join(CapeAnalysis, Artifact.id == CapeAnalysis.artifact_id).filter(CapeAnalysis.cape_status==3).count()

    # get count of ORCA processed samples
    orca_processed = db_session.query(Artifact).join(CapeAnalysis, Artifact.id == CapeAnalysis.artifact_id).filter(CapeAnalysis.orca_status==3).count()

    # get fully processed benign samples
    benign_tag = db_session.query(Tag).filter_by(type='disposition', value='benign').first()
    benign_processed = db_session.query(CapeAnalysis).join(artifact_tags, artifact_tags.c.artifact_id == CapeAnalysis.artifact_id).filter(artifact_tags.c.tag_id == benign_tag.id, CapeAnalysis.orca_status==3).count()


    # get artifact family counts
    family_counts = []
    results = db_session.query(Tag).filter_by(type='family').all()
    families = [(x.id, x.value) for x in results]
    for family in families:
        count = db_session.query(artifact_tags).join(CapeAnalysis, CapeAnalysis.artifact_id==artifact_tags.c.artifact_id).filter(CapeAnalysis.orca_status==3, artifact_tags.c.tag_id==family[0]).count()
        family_counts.append([count, family[1]])

    family_counts = sorted(family_counts,key=lambda x: (x[0],x[1]), reverse=True)
    
    # get signature counts
    signature_counts = []
    results = db_session.query(Tag).filter_by(type='signature_name').all()
    signatures = [(x.id, x.value) for x in results]
    for signature in signatures:
        count = db_session.query(artifact_tags).join(CapeAnalysis, CapeAnalysis.artifact_id==artifact_tags.c.artifact_id).filter(CapeAnalysis.orca_status==3, artifact_tags.c.tag_id==family[0]).count()
        signature_counts.append([count, family[1]])

    signature_counts = sorted(family_counts,key=lambda x: (x[0],x[1]), reverse=True)
    
    # get recent artifact information
    recent_artifacts = []
    artifact_ids = db_session.query(CapeAnalysis.artifact_id).filter_by(cape_status=3, orca_status=3).order_by(CapeAnalysis.artifact_id.desc()).limit(20)
    for row in artifact_ids:
        artifact_id = row[0]
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
        recent_artifacts.append(artifact_info)

    # close cursor (connection is left open in g)
    cur.close()

    return render_template(
        'dashboard.html',
        recent_ids = [x[0] for x in artifact_ids],
        num_tags = '{:,}'.format(num_tags),
        num_artifacts = '{:,}'.format(num_artifacts),
        cape_processed = '{:,}'.format(cape_processed),
        orca_processed = '{:,}'.format(orca_processed),
        benign_processed = benign_processed,
        mal_processed = orca_processed - benign_processed,
        family_counts = family_counts[0:10],
        signature_counts = signature_counts[0:10],
        recent_artifacts = recent_artifacts
    )

