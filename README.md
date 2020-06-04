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
  * [1. Download the Data](#download-the-data)
  * [2. Create Bucket and Push to S3](#2-create-bucket-and-push-to-s3)
  * [3. Create RDS schema](#3-create-rds-schema)
  * [4. Run the Dockerfile](#4-run_the_dockerfile)

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

### 1. Download the data
Since the data is located on Kaggle, you will have to download it directly from the website, located here: https://www.kaggle.com/hugomathien/soccer#database.sqlite

Scroll towards the bottom of the page until you see the "database.sqlite" table. On the right hand side, click the download button. Once downloaded, extract the data from the zip file, and place "database.db" into the data directory of this repo.

### 2. Create Bucket and Push to S3 
First, make sure you are in the root directory of the repository. Then, open src/config.yaml and view the "source_s3" paramaters. Change data_path to the location of the data to be uploaded. Change bucket_name to the name of the S3 bucket that you will upload the data to (Note: if you are creating the bucket from scratch, name the bucket what you would like it to be called). Change database_name to what you would like the database to be called once in S3. If the bucket you are using is in a different location than "us-east-2", change the location parameter as well.

In order to access S3, your aws username and password must be available as environment variables. Create a file named config.env in the root of the repo. Write the following:

aws_access_key_id="YOUR KEY HERE"
aws_secret_access_key="YOUR SECRET KEY HERE"

### 3. Create RDS schema
Once again, open src/config.yaml. This time view the "rds" parameters. If you would like to create the schema in RDS, leave local=False. If you would like to save it locally, switch local to True. If you choose to save locally, change the db_path parameter to the location you would like to save the schema. 

Open up the config.env file you created in step two. Add the following environment variables.
MYSQL_USER="YOUR USER NAME" ##Instructors should be 'msia423instructor'. QA (Josh), yours is 'msia423qa'
MYSQL_PASSWORD="YOUR PASSWORD" ##This should be 'tms5465', for both instructors and QA
MYSQL_HOST=msia423-project.cpqvmnszxomo.us-east-2.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_NAME=fifa

### 4. Run the Dockerfile
Now that the parameters are set, you can create and run the Dockerfile. First, build the image, using the following command.

docker build -t fifa .

Once the Dockerfile is built, run the following command to create a bucket in S3:

docker run --mount type=bind,source="$(pwd)",target=/myapp --env-file=config.env fifa run.py -c

To push data to a bucket that already exists, use the 'p' argument:

docker run --mount type=bind,source="$(pwd)",target=/myapp --env-file=config.env fifa run.py -p

Finally, to create a database schema, use the 'r' argument:

docker run --mount type=bind,source="$(pwd)",target=/myapp --env-file=config.env fifa run.py -r
