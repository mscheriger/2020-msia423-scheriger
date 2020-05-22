import os
import logging
import pandas as pd
import sqlite

def get_table(cur,table):
    '''
    This function fetches the entire table from the database.

    :param cur:   SQLite cursor that connects to the database.
    :param table: String indicating the name of the table to fetch.
    :return:      Pandas DataFrame containing the table.
    '''
    query = 'SELECT * FROM ' + table + ';'
    df = pd.DataFrame(cur.execute(query).fetchall())
    names = list(map(lambda x: x[0], cur.description))
    dic = dict(zip(range(len(names)), names))
    return df.rename(columns=dic)

def winner(df):
    '''
    This function determines who won the match based on the scores.

    :param df: DataFrame of matches. Must contain the home_team_goal and away_team_goal columns.
    :return:   String indicating if match winner was "Home", "Away", or "Draw"

    '''
    assert df.home_team_goal is not None and df.away_team_goal is not None
    if df.home_team_goal > df.away_team_goal:
        answer = 'Home'
    elif df.home_team_goal < df.away_team_goal:
        answer = 'Away'
    else:
        answer = 'Draw'
    return answer

def merge_rating(match_df,player_df,col,newname):
    '''
    This function merges in the overall player ratings into the match dataframe.

    :param match_df:  Dataframe of matches. Must have date variables.
    :param player_df: Dataframe containing all player ratings. Must have date and player_id variables
    :param col:       String indicating name of the column to be merged with
    :param newname:   String indicating the name of the new player rating column

    :return:          Original match dataframe with additional column corresponding to player rating
    '''
    original = match_df.shape[0]
    match_df = match_df.merge(player_df,how='left',left_on=['date',col],right_on=['date','player_id'])
    assert all(match_df.loc[match_df[col].notnull()].overall_rating.isna()==False)
    assert match_df.shape[0]==original
    match_df.rename(columns={'overall_rating':newname},inplace=True)
    match_df.drop(columns='player_id',inplace=True)
    return match_df

def eng_ratings(match_df):
    '''
    This function calculates the average overall player score, as well as the defense, midfield, and offensive average
    Must have the home and away player scores already in the dataframe.

    :param match_df: Dataframe of matches

    :return:         Original dataframe with additional columns of averages for home and away team.
    '''
    final_df = match_df.copy()
    final_df['home_overall_rating'] = match_df[['hp1','hp2','hp3','hp4','hp5','hp6','hp7','hp8','hp9','hp10','hp11']].mean(axis=1)
    final_df['away_overall_rating'] = match_df[['ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8','ap9','ap10','ap11']].mean(axis=1)
    final_df['home_def_rating'] = match_df[['hp2','hp3','hp4','hp5']].mean(axis=1)
    final_df['away_def_rating'] = match_df[['ap2','ap3','ap4','ap5']].mean(axis=1)
    final_df['home_mid_rating'] = match_df[['hp6','hp7','hp8']].mean(axis=1)
    final_df['away_mid_rating'] = match_df[['ap6','ap7','ap8']].mean(axis=1)
    final_df['home_off_rating'] = match_df[['hp9','hp10','hp11']].mean(axis=1)
    final_df['away_off_rating'] = match_df[['ap9','ap10','ap11']].mean(axis=1)
    return final_df

def ewma_score(match_df,a=.5,p=4):
    '''
    This function creates an exponentially weighted moving average of the teams record over the season.

    :param match_df: Dataframe of matches
    :param a: Float indicating the rate of decay for the moving average. Must be >0 and <=1
    :param p: Int indicating how many periods to skip at beginning of season. Default is 4
    '''
    home_teams = match_df[['date','season','home_team_api_id','outcome']].rename(columns={'home_team_api_id':'team_id'})
    home_teams['ewma'] = 0
    home_teams.loc[home_teams.outcome=='Home','ewma']=1
    home_teams.loc[home_teams.outcome=='Away','ewma']=-1
    away_teams = match_df[['date','season','away_team_api_id','outcome']].rename(columns={'away_team_api_id':'team_id'})
    away_teams['ewma'] = 0
    away_teams.loc[away_teams.outcome=='Home','ewma']=-1
    away_teams.loc[away_teams.outcome=='Away','ewma']=1
    all_teams = home_teams.append(away_teams).sort_values(by=['team_id','date'])
    all_teams = all_teams.drop(columns='outcome')
    all_teams['ewma'] = all_teams.groupby(['team_id','season'])['ewma'].transform(lambda v: v.ewm(alpha=a,min_periods=p).mean())
    all_teams = all_teams.fillna(0)

    check_rows = match_df.shape[0]
    check_cols = match_df.shape[1]
    match_df = match_df.merge(all_teams,left_on=['home_team_api_id','season','date'],right_on=['team_id','season','date'],how='left')
    match_df = match_df.rename(columns={'ewma':'home_ewma'})
    match_df = match_df.drop(columns=['team_id'])
    match_df = match_df.merge(all_teams,left_on=['away_team_api_id','season','date'],right_on=['team_id','season','date'],how='left')
    match_df = match_df.rename(columns={'ewma':'away_ewma'})
    match_df = match_df.drop(columns=['team_id'])

    assert check_rows==match_df.shape[0]
    assert check_cols+2==match_df.shape[1]

    return match_df
