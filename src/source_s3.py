# from app import db
# from app.models import Track
import logging.config
import yaml 
import os
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def source_bucket(bucket_name,location='us-east-2'):
    '''
    Creates a bucket in s3. Note that aws credentials must be environment variables.

    @param bucket_name: Name of the bucket to be created
    @param location:    Location server to push the bucket to.
    @return:            None
    '''
    session = boto3.session.Session(aws_access_key_id=os.environ.get("aws_access_key_id"),aws_secret_access_key=os.environ.get("aws_secret_access_key"))
    s3 = session.resource("s3")
    try:
        s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint':location})
        logger.info('Bucket successfully created')
    except ClientError as e:
        logger.error(e)
    pass

def push_data(data_path,bucket_name,data_name):
    '''
    Function pushes data to an S3 bucket.

    @param data_path:   String indicating the location of the file to be pushed.
    @param bucket_name: Name of the bucket
    @param data_name:   Alias of data that will be pushed in S3.
    @return:            None
    '''
    session = boto3.session.Session(aws_access_key_id=os.environ.get("aws_access_key_id"),aws_secret_access_key=os.environ.get("aws_secret_access_key"))
    s3 = session.client('s3')
    try:
        logger.info('Data upload has begun')
        response = s3.upload_file(data_path,bucket_name,data_name)
        logger.info('Data upload has completed successfully')
    except ClientError as e:
        logging.error(e)
    except FileNotFoundError as e1:
        logging.error("Filepath cannot be found.")
    pass

if __name__=='__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config_s3 = config['source_s3']
    source_bucket(config_s3['bucket_name'],config_s3['location'])
    push_data(config_s3['data_path'],config_s3['bucket_name'],config_s3['database_name'])
