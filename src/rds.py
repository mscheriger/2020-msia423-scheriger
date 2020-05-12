import os
import logging
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, MetaData, Float
from sqlalchemy.exc import OperationalError, InternalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()  

class Bets(Base):
    """Create a data model for the database to be set up for Betting on Games """
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, unique=True, nullable=False)
    league_name = Column(String(100),unique=False, nullable=False)
    season = Column(String(100),unique=False, nullable=False)
    home_team = Column(String(100),unique=False, nullable=False)
    away_team = Column(String(100),unique=False, nullable=False)
    prob_home = Column(Float, unique=False, nullable=False)
    prob_away = Column(Float, unique=False, nullable=False)
    prob_draw = Column(Float, unique=False, nullable=False)
    goals_home = Column(Integer, unique=False, nullable=False)
    goals_away = Column(Integer, unique=False, nullable=False)
    outcome = Column(String(100), unique=False, nullable=False)
    bet_on = Column(String(100), unique=False, nullable=False)
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
        database = os.environ.get("MYSQL_NAME")
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
    try:
        # set up mysql connection
        engine = sql.create_engine(engine_string)
        # create the tracks table
        Base.metadata.create_all(engine)
        logger.info('Tables successfully created')
    except OperationalError as e:
        logger.error('Cannot connect to the server. Double check your environment variables.')
    except InternalError as e1:
        logger.error('Cannot find the database. Check the MYSQL_NAME environment variable.')
