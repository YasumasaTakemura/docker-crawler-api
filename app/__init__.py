import os
if '.local' in os.listdir(os.getcwd()):
    os.environ['DATABASE_NAME'] = 'test'