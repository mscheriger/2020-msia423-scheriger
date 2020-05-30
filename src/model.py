import os
import logging
import pandas as pd
from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn.model_selection import RandomizedSearchCV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prep_data(data_location,keep_cols,season='2015/2016'):
    '''
    Function preps data to be analyzed by the model

    @param data_location: Location of the cleaned dataset
    @param keep_cols:     List of columns to be included in the model
    @param season:        Season to be used as the test set
    @return:              The Match dataframe, as well as the test and train datasets
    '''
    try:
        matches = pd.read_csv(data_location)
        matches = matches[keep_cols]
        matches = pd.get_dummies(matches,columns=['league_id'])
        test = matches.loc[matches.season==season]
        train = matches.loc[matches.season!=season]
        test = test.drop(columns='season')
        train = train.drop(columns=['season','id'])
        return matches, train, test
    except FileNotFoundError as e:
        logging.error('Cannot find file')
        return None

def run_model(train,params,objective,num_class,xgb_seed,folds,cv_seed):
    '''
    Function runs an XGBoost Classification model on the training data

    @param train:     Pandas dataframe with training data
    @param params:    Dictionary of parameters to be passed to XGBoost
    @param objective: Objective function to be used
    @param num_class: Number of classes being predicted.
    @param xgb_seed:  Random seed for the model
    @param folds:     Number of folds for cross validation
    @param cv_seed:   Random seed for cross validation.
    @return:          Fitted model object
    '''
    logging.info('Training Model')
    X = train.drop(columns='outcome')
    y = train.outcome
    xgb = XGBClassifier(objective=objective, num_class=num_class, seed=xgb_seed)
    xgb_cv = RandomizedSearchCV(xgb, params,cv=folds,random_state=cv_seed)
    xgb_cv.fit(X, y)

    logger.info('Cross validation accuracy is {}'.format(xgb_cv.best_score_))
    return xgb_cv

def predictions(xgb,test,final_location):
    '''
    Function makes predictions and saves these into a CSV

    @param xgb:            Fitted model object
    @param test:           Test data
    @param final_location: Filepath to save out the predictions
    @return:               None
    '''
    predictions = xgb.predict_proba(test.drop(columns=['outcome','id']))
    predicted = xgb.predict(test.drop(columns=['outcome','id']))
    test['away_prob'] = predictions[:,0]
    test['draw_prob'] = predictions[:,1]
    test['home_prob'] = predictions[:,2]
    test['prediction'] = predicted
    ###Log Test accuracy here
    acc = (test.outcome==test.prediction).sum()/test.shape[0]
    logging.info('Test accuracy is {}'.format(acc))
    test = test[['id','away_prob','draw_prob','home_prob','prediction']]
    test.to_csv(final_location,index=False)

def run_all_model(data_location,keep_cols,season,params,objective,num_class,xgb_seed,folds,cv_seed,final_location):
    '''
    Function runs all functions above sequentially
    @param data_location:  Location of the cleaned dataset
    @param keep_cols:      List of columns to be included in the model
    @param season:         Season to be used as the test set
    @param params:         Dictionary of parameters to be passed to XGBoost
    @param objective:      Objective function to be used
    @param num_class:      Number of classes being predicted.
    @param xgb_seed:       Random seed for the model
    @param folds:          Number of folds for cross validation
    @param cv_seed:        Random seed for cross validation.
    @param final_location: Filepath to save out the predictions
    @return:               None
    '''

    matches, train, test = prep_data(data_location,keep_cols,season)
    xgb = run_model(train,params,objective,num_class,xgb_seed,folds,cv_seed)
    predictions(xgb,test,final_location)
