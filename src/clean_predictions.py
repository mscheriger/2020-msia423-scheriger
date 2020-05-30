import os
import logging
import pandas as pd
import sqlite3
from src.feat_eng import get_table
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def best_line(df,columns):
    '''
    This function takes the matches dataframe and returns the best lines for a given set of columns

    @param df:      Matches dataframe
    @param columns: List of columns which contain the betting lines
    @return:        Float value of the best line
    '''
    df_cols = df[columns].fillna(0)
    return max(df_cols)

def bet_on_profit(df,units=1):
    '''
    This function determines which team to bet on, as well as the profit made

    @param df:    Matches dataframe. Must have the lines calculated and probabilities determined
    @param units: Dollars to be wagered on the match
    @return:      The team to bet on, as well as the money made or lost
    '''

    exp_profit = 0
    bet_on = "None"

    if ((df.home_line-1)*df.home_prob) - (1-df.home_prob) > exp_profit:
        exp_profit = ((df.home_line-1)*df.home_prob) - (1-df.home_prob)
        bet_on = df.home_team_name

    if ((df.away_line-1)*df.away_prob) - (1-df.away_prob) > exp_profit:
        exp_profit = ((df.away_line-1)*df.away_prob) - (1-df.away_prob)
        bet_on = df.away_team_name

    if ((df.draw_line-1)*df.draw_prob) - (1-df.draw_prob) > exp_profit:
        exp_profit = ((df.draw_line-1)*df.draw_prob) - (1-df.draw_prob)
        bet_on = "Draw"

    if bet_on==df.team_outcome and df.outcome=="Home":
        profit = (df.home_line-1)*units
    elif bet_on==df.team_outcome and df.outcome=="Away":
        profit = (df.away_line-1)*units
    elif bet_on==df.team_outcome and df.outcome=="Draw":
        profit = (df.draw_line-1)*units
    elif bet_on=="None":
        profit = 0
    else:
        profit = -1*units

    return bet_on, exp_profit, profit

def get_team_names(db_location):
    '''
    Function creates a dictionary of team id and team name
    
    @param db_location: location of the database
    @return:            Dictionary with team id as keys and team names as values
    '''
    conn = sqlite3.connect(db_location)
    cur = conn.cursor()
    df_team = get_table(cur,"Team")
    return {key: val for key,val in zip(df_team.team_api_id, df_team.team_short_name)}

def outcome_helper(df):
    '''
    Helper function to determine name of the winner of the match

    @param df: Dataframe of matches. Must have outcome, home_team_name, and away_team_name column
    @return:   Name of the winner of the match
    '''

    if df.outcome=="Away":
        return df.away_team_name
    elif df.outcome=="Home":
        return df.home_team_name
    else:
        return "Draw"

def clean_pred(pred_location,data_location,csv_location,home_lines,draw_lines,away_lines,db_location,keep_cols):
    '''
    Function merges predictions with match data and outputs relevant columns for RDS instance

    @param pred_location: Location of predictions
    @param data_location: Location of matches
    @param csv_location:  Final location to save csv
    @param home_lines:    Column names that contain the home lines
    @param draw_lines:    Column names that contain the draw lines
    @param away_lines:    Column names that contain the away lines
    @param db_location:   Location of the original database
    @param keep_cols:     Final columns to keep for RDS instance
    @return:              None
    '''

    preds = pd.read_csv(pred_location)
    matches = pd.read_csv(data_location)
    team_dic = get_team_names(db_location)
    before = preds.shape[0]
    clean_preds = preds.merge(matches,how='inner',on='id')
    assert clean_preds.shape[0]==before

    clean_preds['home_line'] = clean_preds.apply(best_line,axis=1,columns=home_lines)
    clean_preds['draw_line'] = clean_preds.apply(best_line,axis=1,columns=draw_lines)
    clean_preds['away_line'] = clean_preds.apply(best_line,axis=1,columns=away_lines)

    clean_preds['home_team_name'] = clean_preds.apply(lambda x: team_dic.get(x.home_team_api_id),axis=1)
    clean_preds['away_team_name'] = clean_preds.apply(lambda x: team_dic.get(x.away_team_api_id),axis=1)
    
    clean_preds['team_outcome'] = clean_preds.apply(outcome_helper,axis=1)
    bets = clean_preds.apply(bet_on_profit,axis=1)
    clean_preds['bet_on'] = pd.Series([x[0] for x in bets])
    clean_preds['exp_profit'] = pd.Series([x[1] for x in bets])
    clean_preds['profit'] = pd.Series([x[2] for x in bets])
    clean_preds = clean_preds[keep_cols]
    clean_preds['date'] = clean_preds.apply(lambda x: datetime.strptime(x.date[:10],"%Y-%m-%d"),axis=1)
    clean_preds = clean_preds.sort_values(by=['league_id','date','home_team_name'])
    clean_preds.to_csv(csv_location,index=False)
