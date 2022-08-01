import os

from flask import Flask

from app.settings import CAPE_PORT, CAPE_URL, JUPYTER_SERVER

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        CAPE_URL = CAPE_URL,
        CAPE_PORT = CAPE_PORT,
        JUPYTER_SERVER = JUPYTER_SERVER
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('settings.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # register dashboard
    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')
    
    # register artifact
    from . import artifact
    app.register_blueprint(artifact.bp)
    app.add_url_rule('/artifact', endpoint='artifact')

    # register tag
    from . import tag
    app.register_blueprint(tag.bp)
    app.add_url_rule('/tag', endpoint='tag')

    # register search
    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule('/search', endpoint='search')

    return app