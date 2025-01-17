# MSiA423 Project - European Soccer Predictions
### Michael Scheriger
### QA: Josh Kornblatt
<!-- toc -->

- [Directory structure](#directory-structure)
- [Charter](#charter)
- [Disclaimer](#disclaimer)
- [Conclusion](#conclusion)
- [Running the app](#running-the-app)
  * [1. Download the Data](#download-the-data)
  * [2. Create Bucket and Push to S3](#2-create-bucket-and-push-to-s3)
  * [3. Create RDS schema](#3-create-rds-schema)
  * [4. Run the Dockerfile](#4-run_the_dockerfile)
  * [5. Run the App](#5-run_the_app)
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
Develop a profitable method for betting on European soccer matches using FIFA ratings.

### Mission
Create an app where the user selects the European soccer league, and the app determines who the user should bet on for each game in 2016. The app will use a machine learning model using FIFA ratings to accurately predict outcomes of European soccer matches. The app will then select wager and bookmaker such that expected profit is maximized, and the user will see how this strategy performed in 2016. The data to be used contains match results for all European soccer matches from 2008 - 2016, corresponding FIFA ratings, and odds from 10 different bookmakers. The database can be found here: https://www.kaggle.com/hugomathien/soccer.

### Success Criteria
#### 1. Profit
The project will truly be successful if we can demonstrate that a strategy using a model based on FIFA ratings can turn a profit.
#### 2. CCR
In order to turn a profit, the machine learning model must have a superior accuracy to the bookmakers. Therefore, maximizing CCR will lead to a higher profit. According to the data source, bookmakers correctly predict the outcome (win/lose/draw) 53% of the time. Any results greater than this will be sufficient. 

## Disclaimer
In order to be able to run all possible commands using the Dockerfile and reproduce the results, you will require an S3 bucket as well as an RDS instance.

## Conclusion
The final model was an XGBoost classification tree that yielded an accuracy in 2016 of 51%. While this was below the target of 53%, the model did produce a modest profit. The most important features were the exponentially weighted moving average of the teams' recent performances, where a win counted as 1, a tie counted as 0, and a loss counted as -1 (see src/feat_eng.py).

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
```bash
docker build -t fifa .
```

In order to actually run the Dockerfile, type the following:

```bash
docker run --mount type=bind,source="$(pwd)",target=/myapp --env-file=config.env fifa run.py
```

Running the above won't acually run anything - you have to pass specific arguments. See the arguments below.
 -  -c: create a bucket in S3
 -  -p: Push data to S3 bucket
 -  -f: Fetch the data from the S3 bucket
 -  -r: Create the RDS database schema
 -  -e: Perform feature engineering
 -  -m: Run the model
 -  -x: Clean the predictions from the model
 -  -a: Add the data to the RDS instance
 -  -w: Run the entire model pipeline
 -  --db_location: Name of the local database (rather than RDS)

If you would like to use a local database (rather than rds), pass in the location of the database at the end of the Dockerfile. For example, if you have already run the model pipeline (see below) and would like to push those results to a local database, run the following and replace "my_database_name" with the name of your location:

```bash
docker run --mount type=bind,source="$(pwd)",target=/myapp fifa run.py -r -a --db_location my_database_name
```

To run the entire pipleline, run the following (you can manually input the environment variables rather than setting up a config.env file):

```bash
docker run --mount type=bind,source="$(pwd)",target=/myapp --env-file=config.env fifa run.py -w
```

To run unit tests, run the following:

```bash
docker run fifa -m pytest
```

Note: if tests fail, be sure that all model outputs exist and try again. You may need to rerun the Docker commands from above.

### 5. Run the app
Once the results from the model have been pushed to the RDS instance, run the following commands:

```bash
docker build -f app/Dockerfile -t flask .

docker run -p 5000:5000 --env-file=config.env flask app.py
```
Like before, you can manually enter the environment variables using the -e argument rather than the --env-file argument. If you would like to use a local database as opposed to the RDS instance to run the app, be sure to add the SQLALCHEMY_DATABASE_URI environment variable

Then open port 5000 in your local browser and enjoy the app! (Don't forget to kill the container when you're done)
