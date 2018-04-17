# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db


app = Flask(__name__)
app.config['PROJECT_ID'] = os.getenv('PROJECT_ID')

if not app.config.get('TESTING'):
    # Attaches a Google Stackdriver logging handler to the root logger
    client = google.cloud.logging.Client(app.config['PROJECT_ID'])
    client.setup_logging()
    logger = logging.getLogger('LoggingTest')
    logger.info("API manager is running {}".format(str(datetime.now())))

else :
    logger = logging.getLogger('LoggingTest')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('test.log')
    logger.addHandler(fh)


modules_define = [db.app]
for _app in modules_define:
    app.register_blueprint(_app)


