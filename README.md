# MSiA423 Project - European Soccer Predictions
### Michael Scheriger
### QA: Josh Kornblatt
<!-- toc -->

- [Directory structure](#directory-structure)
- [Charter](#charter)
- [Planning](#planning)
- [Backlog](#backlog)
- [Icebox](#icebox)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```
## Charter
### Vision
Develop a profitable method for betting on European soccer matches.

### Mission
Create an app where the user selects the European soccer league, and the app determines who the user should bet on for each game in 2016. The app will use a machine learning model using FIFA ratings to accurately predict outcomes of European soccer matches. The app will then select wager and bookmaker such that expected profit is maximized, and the user will see how this strategy performed in 2016. The data to be used contains match results for all European soccer matches from 2008 - 2016, corresponding FIFA ratings, and odds from 10 different bookmakers. The database can be found here: https://www.kaggle.com/hugomathien/soccer.

### Success Criteria
#### 1. Profit
The project will truly be successful if we can demonstrate that a strategy using a model based on FIFA ratings can turn a profit.
#### 2. CCR
In order to turn a profit, the machine learning model must have a superior accuracy to the bookmakers. Therefore, maximizing CCR will lead to a higher profit. According to the data source, bookmakers correctly predict the outcome (win/lose/draw) 53% of the time. Any results greater than this will be sufficient. 

## Planning

### Initiative
Develop a model that allows the user to profitably gamble on European soccer matches.

### Epics and Stories
#### Epic 1. Pipeline: Construct a data pipeline that allows for rapid model development.
 -  Story 1: Merge relevant data tables together and clean them in order to be ready for model training. 
 -  Story 2: Assess robustness of data for each year and league - is there enough to make predictions?  
 -  Story 3: Develop pipeline so that data can be pulled regardless of host
 -  Story 4: Expand pipeline to include data through 2020. Will need to explore other datasets/APIs.
 
#### Epic 2. Model: Develop a machine learning model that predicts match outcomes.
 - Story 1: Perform exploratory data analysis to check missing values and interactions between variables that may affect the model.
 - Story 2: Engineer features such as FIFA rating by position, moving average of wins, goals for, goals against, etc.
 - Story 3: Create functionality to train model on data from 2008 - 2014, and test on 2015, as well as predicting results for 2016. 
 - Story 4: Develop functionality to train model based on league selected by user. 
 - Story 5: Iterate in order to improve model until threshold of 53% CCR has been met.
  
#### Epic 3. App: Create application to show user which outcomes to bet on.
 - Story 1. Create interface to display model predictions as well as actual outcomes.
 - Story 2. Add additional functionality to allow user to select which European league to predict. 
 - Story 3. Display total net profit if one unit was wagered on every game.
 - Story 4. Use D3 to visualize matches where the model outperformed the bookkeepers, as well as improvements that can be made. 
## Backlog
In order of priority:
1. Pipeline.Story1 (4 points) - PLANNED
2. Pipeline.Story2 (1 point) - PLANNED
3. Model.Story1 (2 points) - PLANNED
3. Model.Story2 (4 points) - PLANNED
4. Pipeline.Story3 (8 points)
5. Model.Story3 (4 points)
6. Model.Story4 (2 points)
7. Model.Story5 (4 points)
8. App.Story1 (8 points)
9. App.Story2 (4 points)
10. App.Story3 (2 points)

## Icebox
1. Pipeline.Story4
2. App.Story4

## Running the app
### 1. Initialize the database 

#### Create the database with a single song 
To create the database in the location configured in `config.py` with one initial song, run: 

`python run.py create_db --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py create_db` creates a database at `sqlite:///data/tracks.db` with the initial song *Radar* by Britney spears. 
#### Adding additional songs 
To add an additional song:

`python run.py ingest --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py ingest` adds *Minor Cause* by Emancipator to the SQLite database located in `sqlite:///data/tracks.db`.

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker 

### 1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
### 2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.