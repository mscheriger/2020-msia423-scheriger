import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
from src.rds import Bets
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

print("This is working")
# Initialize the Flask application
app = Flask("fifa", template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

# Initialize the database
db = SQLAlchemy(app)

@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """
    
    try:
        bet_data = db.session.query(Bets).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html', bets=bet_data, league="All",total=0)
    except:
        traceback.print_exc()
        logger.warning("Not able to display tracks, error page returned")
        return render_template('error.html')


@app.route('/choose', methods=['POST'])
def choose_table():
    """View that process a POST with new song input

    :return: redirect to index page
    """

    if request.form['button']== 'Premier League':
        bet_data = db.session.query(Bets).filter(Bets.league_id==1729)
        total_profit = db.session.query(func.sum(Bets.profit)).filter(Bets.league_id==1729).scalar()
    elif request.form['button']== 'Bundesliga':
        bet_data = db.session.query(Bets).filter(Bets.league_id==7809)
        total_profit = db.session.query(func.sum(Bets.profit)).filter(Bets.league_id==7809).scalar()
    elif request.form['button']== 'French Ligue 1':
        bet_data = db.session.query(Bets).filter(Bets.league_id==4769)
        total_profit = db.session.query(func.sum(Bets.profit)).filter(Bets.league_id==4769).scalar()
    elif request.form['button']== 'La Liga':
        bet_data = db.session.query(Bets).filter(Bets.league_id==21518)
        total_profit = db.session.query(func.sum(Bets.profit)).filter(Bets.league_id==21518).scalar()
    elif request.form['button']== 'Serie A':
        bet_data = db.session.query(Bets).filter(Bets.league_id==10257)
        total_profit = db.session.query(func.sum(Bets.profit)).filter(Bets.league_id==10257).scalar()
    return render_template('index.html', bets=bet_data, league=request.form['button'],total=total_profit)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
