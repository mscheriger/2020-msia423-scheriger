import os
import yaml

###READ CONFIG FILE
try:
    with open('src/config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError as e:
    logger.error('Cannot find Config File')
    exit()
config_rds = config['rds']

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000 
APP_NAME = "fifa"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
if DB_PORT is not None:
    DB_PORT = int(DB_PORT)
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('MYSQL_DATABASE')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    if DB_HOST is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(config_rds['db_path'])
    else:
        SQLALCHEMY_DATABASE_URI = '{dialect}://{user}:{pw}@{host}:{port}/{db}'.format(dialect=DB_DIALECT, user=DB_USER,
                                                                                  pw=DB_PW, host=DB_HOST, port=DB_PORT,
                                                                                  db=DATABASE)
