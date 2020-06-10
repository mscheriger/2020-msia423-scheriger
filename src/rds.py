import os
import logging
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, MetaData, Float
from sqlalchemy.exc import OperationalError, InternalError, IntegrityError
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()  

class Bets(Base):
    """Create a data model for the database to be set up for Betting on Games """
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, unique=True, nullable=False)
    league_id = Column(Integer,unique=False, nullable=False)
    season = Column(String(100),unique=False, nullable=False)
    date = Column(String(100),unique=False, nullable=False)
    home_team = Column(String(100),unique=False, nullable=False)
    away_team = Column(String(100),unique=False, nullable=False)
    home_line = Column(Float, unique=False, nullable=False)
    draw_line = Column(Float, unique=False, nullable=False)
    away_line = Column(Float, unique=False, nullable=False)
    prob_home = Column(Float, unique=False, nullable=False)
    prob_away = Column(Float, unique=False, nullable=False)
    prob_draw = Column(Float, unique=False, nullable=False)
    goals_home = Column(Integer, unique=False, nullable=False)
    goals_away = Column(Integer, unique=False, nullable=False)
    outcome = Column(String(100), unique=False, nullable=False)
    bet_on = Column(String(100), unique=False, nullable=False)
    exp_profit = Column(Float, unique=False, nullable=False)
    profit = Column(Float, unique=False, nullable=False)
 
    def __repr__(self):
        return '<Bets %r>' % self.match_id

def create_table(local=False,local_location=None):
    '''
    Function creates the tables of a mySQL DB Instance defined
    
    @param local:          Boolean indicating if the table should be created locally or on RDS
    @param local_location: File path if the database is to be created locally
    @return:               None
    '''
    if local:
        engine_string = 'sqlite:///{}'.format(local_location)
    else:
        conn_type = "mysql+pymysql"
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")
        database = os.environ.get("MYSQL_DATABASE")
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
    try:
        # set up mysql connection
        engine = sql.create_engine(engine_string)
        Base.metadata.drop_all(engine)
        # create the tracks table
        Base.metadata.create_all(engine)
        logger.info('Tables successfully created')
    except OperationalError as e:
        logger.error('Cannot connect to the server. Double check your environment variables and make sure you are connected to the NU VPN.')
    except InternalError as e1:
        logger.error('Cannot find the database. Check the MYSQL_NAME environment variable.')

def add_data(df_location,local=False,local_location=None):
    '''
    Function adds data to an RDS instance. 

    @param df_location: CSV location of the data to be added
    @return:            None
    '''
    if local:
        engine_string = 'sqlite:///{}'.format(local_location)
    else:
        conn_type = "mysql+pymysql"
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")
        database = os.environ.get("MYSQL_DATABASE")
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
    try:
        # set up mysql connection
        engine = sql.create_engine(engine_string)
    except OperationalError as e:
        logger.error('Cannot connect to the server. Double check your environment variables and make sure you are connected to the NU VPN.')
    except InternalError as e1:
        logger.error('Cannot find the database. Check the MYSQL_DATABASE environment variable.')

    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.read_csv(df_location)
    logger.info('Adding data to RDS instance')
    counter = 0
    for index, row in df.iterrows():
        bet = Bets(match_id=row['id'], league_id = row['league_id'], season = row['season'], date = row['date'], home_team = row['home_team_name'], away_team = row['away_team_name'], home_line = row['home_line'], draw_line = row['draw_line'], away_line = row['away_line'], prob_home = row['home_prob'], prob_away = row['away_prob'], prob_draw = row['draw_prob'], goals_home = row['home_team_goal'], goals_away = row['away_team_goal'], outcome = row['team_outcome'], bet_on = row['bet_on'], exp_profit = row['exp_profit'], profit=row['profit'])
        try:
            logging.debug(bet)
            session.add(bet)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            counter += 1
    if counter >0:
        logging.info('{} rows already in database and were not added'.format(counter))

