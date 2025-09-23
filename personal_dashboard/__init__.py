from flask import Flask
import os
from dotenv import load_dotenv
from os.path import join, dirname

def create_app():
    dotenv_path = join(dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    app = Flask(__name__.split('.')[0], static_folder='../static', static_url_path='/static')
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DEBUG'] = True

    from . import routes
    app.register_blueprint(routes.bp)

    return app
