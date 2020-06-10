import pytest
import pandas as pd
from src.model import prep_data, run_model, predictions

def test_prep_data_good():
    ##Note - feature engineering module must have been run prior
    location = 'data/clean_matches.csv'
    keep_cols = ['id','league_id', 'season', 'outcome', 'hp1', 'ap1', 'hp2', 'ap2', 'hp3', 'ap3', 'hp4', 'ap4', 'hp5', 'ap5', 'hp6', 'ap6', 'hp7', 'ap7', 'hp8', 'ap8', 'hp9', 'ap9', 'hp10', 'ap10', 'hp11', 'ap11', 'home_overall_rating', 'away_overall_rating', 'home_def_rating', 'away_def_rating', 'home_mid_rating', 'away_mid_rating', 'home_off_rating', 'away_off_rating', 'home_ewma', 'away_ewma']
    
    matches, train, test = prep_data(location,keep_cols)
    assert test.shape[0]==1826

def test_prep_data_bad():
    location='broken'
    keep_cols = ['id','league_id', 'season', 'outcome', 'hp1', 'ap1', 'hp2', 'ap2', 'hp3', 'ap3', 'hp4', 'ap4', 'hp5', 'ap5', 'hp6', 'ap6', 'hp7', 'ap7', 'hp8', 'ap8', 'hp9', 'ap9', 'hp10', 'ap10', 'hp11', 'ap11', 'home_overall_rating', 'away_overall_rating', 'home_def_rating', 'away_def_rating', 'home_mid_rating', 'away_mid_rating', 'home_off_rating', 'away_off_rating', 'home_ewma', 'away_ewma']
    assert prep_data(location,keep_cols)==None

def test_run_model():
    data= [[1,1,2,3,"1"],[2,2,3,3,"1"],[3,4,5,6,"2"]]
    df = pd.DataFrame(data,columns=['z','a','b','c','outcome'])
    params={'min_child_weight':[1,2,3,4,5], 'gamma':[.3,.4,.5],  'subsample':[.6,.7,.8,.9,1],'colsample_bytree':[.6,.7,.8,.9,1], 'max_depth': [2,3,4]}
    objective = 'multi:softmax'
    num_class = 2
    seed = 1
    mod = run_model(df,params,objective,num_class,seed,2,seed)
    assert abs(mod.best_score_-(2/3))<.0001

def test_predictions():
    data= [[1,2,3,"away"],[2,3,3,"away"],[4,5,6,"draw"],[4,5,7,"home"]]
    df = pd.DataFrame(data,columns=['a','b','c','outcome'])
    params={'min_child_weight':[1,2,3,4,5], 'gamma':[.3,.4,.5],  'subsample':[.6,.7,.8,.9,1],'colsample_bytree':[.6,.7,.8,.9,1], 'max_depth': [2,3,4]}
    objective = 'multi:softmax'
    num_class = 3
    seed = 1
    mod = run_model(df,params,objective,num_class,seed,2,seed)

    test_data = [[4,3,4,5,"draw"]]
    test = pd.DataFrame(test_data,columns=['id','a','b','c','outcome'])
    prediction = predictions(mod,test)
    assert abs(prediction.away_prob[0]-0.474253)<.0001
