# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db

app = Flask(__name__)
# app.config['PROJECT_ID'] = os.getenv('PROJECT_ID')

client = google.cloud.logging.Client()
client.setup_logging(logging.INFO)
logger = logging.getLogger('LoggingTest')
logger.setLevel(logging.INFO)

# if not app.testing :
#
# else:
#     logger = logging.getLogger('LoggingTest')
#     logger.setLevel(logging.INFO)
#     fh = logging.FileHandler('test.log')
#     logger.addHandler(fh)



modules_define = [db.app]
for _app in modules_define:
    app.register_blueprint(_app)
