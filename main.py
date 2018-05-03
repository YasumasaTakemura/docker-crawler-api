# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db
from app.search_console_test import view as test_app

app = Flask(__name__)

modules_define = [db.app,test_app.app]
for _app in modules_define:
    app.register_blueprint(_app)

try:
    client = google.cloud.logging.Client(os.environ.get('PROJECT_ID'))
    print(client._credentials)
    client.setup_logging(logging.INFO)
    logger = logging.getLogger('LoggingTest')
    logger.setLevel(logging.INFO)
    logger.info('entry')
except:
    pass


app.run(debug=True)