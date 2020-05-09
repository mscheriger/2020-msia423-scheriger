from src.source_s3 import source_bucket, push_data
import yaml 
import logging.config

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

if __name__ == '__main__':
    '''
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers()

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--artist", default="Britney Spears", help="Artist of song to be added")
    sb_create.add_argument("--title", default="Radar", help="Title of song to be added")
    sb_create.add_argument("--album", default="Circus", help="Album of song being added.")
    sb_create.add_argument("--engine_string", default='sqlite:///data/tracks.db',
                           help="SQLAlchemy connection URI for database")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--artist", default="Emancipator", help="Artist of song to be added")
    sb_ingest.add_argument("--title", default="Minor Cause", help="Title of song to be added")
    sb_ingest.add_argument("--album", default="Dusk to Dawn", help="Album of song being added")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/tracks.db',
                           help="SQLAlchemy connection URI for database")
    sb_ingest.set_defaults(func=add_track)

    args = parser.parse_args()
    args.func(args)
    '''
    if __name__=='__main__':
        ###READ CONFIG FILE
        try:
            with open('src/config.yaml', 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            logger.error('Cannot find Config File')
            exit()
        config_s3 = config['source_s3']
        
        ###CREATE BUCKET AND PUSH DATABASE TO S3
        source_bucket(config_s3['bucket_name'],config_s3['location'])
        push_data(config_s3['data_path'],config_s3['bucket_name'],config_s3['database_name'])

