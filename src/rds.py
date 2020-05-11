import os
import logging
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, MetaData, Float

conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("MYSQL_NAME")
engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)

Base = declarative_base()  

class Bets(Base):
    """Create a data model for the database to be set up for Betting on Games """
    __tablename__ = 'bets'
    match_id = Column(Integer, primary_key=True)
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

def create_table(base_class=Bets,local=False):
    '''
    Function creates an instance of a mySQL table
    
    @param base_class: Class of the schema to be created
    @param local:      Boolean indicating if the table should be created locally or on RDS
    @return:           None
    '''

    # set up mysql connection
    engine = sql.create_engine(engine_string)
    print('working')
    print(engine)
    # create the tracks table
    Base.metadata.create_all(engine)
    pass

'''
# set up looging config
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

# create a db session
Session = sessionmaker(bind=engine)  
session = Session()


# add a record/track
track1 = Track(artist="Britney Spears", album="Circus", title="Radar")  
session.add(track1)
session.commit()

logger.info("Database created with song added: Radar by Britney spears from the album, Circus")  
track2 = Track(artist="Tayler Swift", album="Red", title="Red")  
session.add(track2)

# To add multiple rows
# session.add_all([track1, track2])


session.commit()   
logger.info("Database created with song added: Red by Tayler Swift from the album, Red")

# query records
track_record = session.query(Track.title, Track.album).filter_by(artist="Britney Spears").first() 
print(track_record)

query = "SELECT * FROM tracks WHERE artist LIKE '%%Britney%%'"
result = session.execute(query)
print(result.first().items())

session.close()
'''
