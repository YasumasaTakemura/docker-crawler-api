# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db

app = Flask(__name__)

client = google.cloud.logging.Client(os.environ.get('PROJECT_ID'))
print(client._credentials)
client.setup_logging(logging.INFO)
logger = logging.getLogger('LoggingTest')
logger.setLevel(logging.INFO)

logger.info('entry')

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
