"""
Dashboard Blueprint for artifact view
"""

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app, request
from sqlalchemy import or_

from app.database import get_db_session, get_db_connection
from app.mappings_orca import Artifact, Tag, artifact_tags
from app.mappings_cape import CapeAnalysis

bp = Blueprint('search', __name__)


# artifact page
@bp.route('/search', methods=['post'], strict_slashes=False)
def search():
    
    # perform search
    db_con = get_db_connection()
    cur = db_con.cursor()
    term = request.form['q']

    stmt = "SELECT id, type, value FROM tags WHERE __ts_vector__ @@ phraseto_tsquery('english', %s) LIMIT 1000;"
    cur.execute(stmt, (term,) )
    tags_t = cur.fetchall()

    if not tags_t:
        return render_template('search.html', tags=None, term=term)
    # get tags associated with artifact
    args = ", ".join([str(t[0]) for t in tags_t])

    # get artifacts counts for each associated tag
    stmt = f'SELECT tag_id, count(*) FROM artifacts_tags WHERE tag_id IN ({args}) GROUP BY (tag_id);'
    cur.execute(stmt)
    results = cur.fetchall()

    # combine counts with tags
    tags = []
    for idx in range(len(results)):
        tags.append((tags_t[idx][0], tags_t[idx][1], tags_t[idx][2], results[idx][1]))



    return render_template('search.html', tags=tags, term=term)
    