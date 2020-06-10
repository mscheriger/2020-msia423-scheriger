from src.source_s3 import source_bucket, push_data, get_data
from src.rds import create_table, add_data
from src.feat_eng import run_all_feat_eng
from src.model import run_all_model
from src.clean_predictions import clean_pred
import yaml 
import logging.config
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    parser.add_argument('-c', '--create_bucket', action='store_true', default=False, help='If given, a new bucket will be created.')
    parser.add_argument('-p', '--push_to_bucket', action='store_true', default=False, help='If given, data will be pushed to S3 bucket.')
    parser.add_argument('-f', '--fetch_data', action='store_true', default=False, help='If given, data will be fetched from S3 bucket.')
    parser.add_argument('-r', '--rds_schema', action='store_true', default=False, help='If given, schema for database will be created.')
    parser.add_argument('-e', '--engineer', action='store_true', default=False, help='If given, performs data cleaning and feature engineering.')
    parser.add_argument('-m', '--model', action='store_true', default=False, help='If given, runs model on clean data.')
    parser.add_argument('-x', '--clean_preds', action='store_true', default=False, help='If given, clean predictions from model')
    parser.add_argument('-a', '--add_data', action='store_true', default=False, help='If given, adds data to the RDS instance')
    parser.add_argument('-w','--whole_pipeline',action='store_true', default=False, help='Run the entire model pipeline. Pull data from S3, feature engineering, model, clean predictions')
    parser.add_argument('--db_location', default=None, help='If using a local database (rather than RDS), pass the file location here')
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
    config_feat = config['feat_eng']
    config_model = config['model']
    config_pred = config['clean_pred']

    ###Change location to local
    if args.db_location is not None:
        config_rds['local'] = True
        config_rds['db_path'] = args.db_location
    
    ###CREATE BUCKET AND PUSH DATABASE TO S3
    if args.create_bucket:
        source_bucket(config_s3['bucket_name'],config_s3['location'])
    if args.push_to_bucket:
        push_data(config_s3['data_path'],config_s3['bucket_name'],config_s3['database_name'])
    if args.fetch_data or args.whole_pipeline:
        get_data(config_s3['bucket_name'],config_s3['database_name'],config_s3['local_location'])

    ###Create RDS Schema
    if args.rds_schema:
        create_table(local=config_rds['local'],local_location=config_rds['db_path'])

    ###Data CLEANING AND FEATURE ENGINEERING
    if args.engineer or args.whole_pipeline:
        run_all_feat_eng(config_feat['data_location'],config_feat['final_location'],config_feat['league_ids'],config_feat['droplabels'])

    ###Run the model
    if args.model or args.whole_pipeline:
        run_all_model(config_model['data_location'],config_model['keep_cols'],config_model['season'],config_model['params'],config_model['objective'],config_model['num_class'],config_model['seed_xgb'],config_model['cv'],config_model['seed_cv'],config_model['final_location'])
    
    ###Clean predictions
    if args.clean_preds or args.whole_pipeline:
        clean_pred(config_pred['pred_location'],config_pred['data_location'],config_pred['csv_location'],config_pred['home_lines'],config_pred['draw_lines'],config_pred['away_lines'],config_pred['db_location'],config_pred['keep_cols'])
    
    ###Add data to RDS
    if args.add_data:
        add_data(config_rds['pred_location'],local=config_rds['local'],local_location=config_rds['db_path'])
