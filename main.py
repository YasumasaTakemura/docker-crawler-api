# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from flask import Flask
import google.cloud.logging
from app.db_connector import view as db
from env import settings

settings.load_dotenv()

logger = logging.getLogger('LoggingTest')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('test.log')
logger.addHandler(fh)


logger.info("info message")

app = Flask(__name__)
app.config['PROJECT_ID'] = os.getenv('PROJECT_ID')

if not app.testing:
    # Attaches a Google Stackdriver logging handler to the root logger
    client = google.cloud.logging.Client(app.config['PROJECT_ID'])
    client.setup_logging()

logger.info("API manager is running {}".format(str(datetime.now())))

modules_define = [db.app]
for _app in modules_define:
    app.register_blueprint(_app)


