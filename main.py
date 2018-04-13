# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db
from env import settings

app = Flask(__name__)
settings.load_dotenv()
app.config['PROJECT_ID'] = os.getenv('PROJECT_ID')

if not app.testing:
    # Attaches a Google Stackdriver logging handler to the root logger
    client = google.cloud.logging.Client(app.config['PROJECT_ID'])
    client.setup_logging(logging.INFO)


modules_define = [db.app]
for _app in modules_define:
    app.register_blueprint(_app)
