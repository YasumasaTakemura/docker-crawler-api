# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db

app = Flask(__name__)
app.config['PROJECT_ID'] = os.getenv('PROJECT_ID')

logger = logging.getLogger('LoggingTest')
logger.setLevel(logging.INFO)

if not app.testing :
    client = google.cloud.logging.Client(app.config['PROJECT_ID'])
    client.setup_logging(logging.INFO)
else:
    fh = logging.FileHandler('test.log')
    logger.addHandler(fh)


modules_define = [db.app]
for _app in modules_define:
    app.register_blueprint(_app)
