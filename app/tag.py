"""
Dashboard Blueprint for artifact view
"""

from random import seed
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from sqlalchemy import or_

from app.database import get_db_session, get_db_connection
from app.mappings_orca import Artifact, Tag, artifact_tags
from app.mappings_cape import CapeAnalysis

bp = Blueprint('tag', __name__)


# tag page
@bp.route('/tag/<int:tag_id>', methods=['GET'], strict_slashes=False)
@bp.route('/tag', methods=['GET'], strict_slashes=False)
def tag(tag_id=None):

    # return template is no id
    if tag_id is None:
        return  render_template('tag.html')

    # get tag information
    db_session = get_db_session()
    tag = db_session.query(Tag).filter_by(id=tag_id).first()

    # get artifact count
    artifact_count = db_session.query(artifact_tags).filter(artifact_tags.c.tag_id==tag_id).count()


    # get artifacts associated with tag
    artifacts = db_session.query(Artifact).join(artifact_tags, artifact_tags.c.artifact_id==Artifact.id).filter(artifact_tags.c.tag_id==tag_id).all()


    return render_template(
        'tag.html',
        tag_id = tag_id,
        tag = tag,
        artifact_count = artifact_count,
        artifacts = artifacts
    )
