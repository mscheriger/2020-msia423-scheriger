from src.source_s3 import source_bucket, push_data
from src.rds import create_table
import yaml 
import logging.config
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    parser.add_argument('-c', '--create_bucket', action='store_true', default=False, help='If given, a new bucket will be created.')
    parser.add_argument('-p', '--push_to_bucket', action='store_true', default=False, help='If given, data will be pushed to S3 bucket.')
    parser.add_argument('-r', '--rds_schema', action='store_true', default=False, help='If given, schema for database will be created.'
    args = parser.parse_args()

    ###READ CONFIG FILE
    try:
        with open('src/config.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        logger.error('Cannot find Config File')
        exit()
    config_s3 = config['source_s3']
    config_rds = config['rds'] 
    
    ###CREATE BUCKET AND PUSH DATABASE TO S3
    if args.create_bucket:
        source_bucket(config_s3['bucket_name'],config_s3['location'])
    if args.push_to_bucket:
        push_data(config_s3['data_path'],config_s3['bucket_name'],config_s3['database_name'])

    ###Create RDS Schema
    if args.rds_schema:
        create_table(local=config_rds['local'],local_location=config_rds['db_path'])
