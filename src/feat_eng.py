import os
import logging
import pandas as pd
import sqlite3

def get_table(cur,table):
    '''
    This function fetches the entire table from the database.

    :param cur:   SQLite cursor that connects to the database.
    :param table: String indicating the name of the table to fetch.
    :return:      Pandas DataFrame containing the table.
    '''
    try:
        query = 'SELECT * FROM ' + table + ';'
        df = pd.DataFrame(cur.execute(query).fetchall())
        names = list(map(lambda x: x[0], cur.description))
        dic = dict(zip(range(len(names)), names))
        return df.rename(columns=dic)
    except sqlite3.OperationalError as e:
        logging.error(e)
        return None

def winner(df):
    '''
    This function determines who won the match based on the scores.

    :param df: DataFrame of matches. Must contain the home_team_goal and away_team_goal columns.
    :return:   String indicating if match winner was "Home", "Away", or "Draw"

    '''
    if df.home_team_goal > df.away_team_goal:
        answer = 'Home'
    elif df.home_team_goal < df.away_team_goal:
        answer = 'Away'
    else:    
        answer = 'Draw'
    return answer

def merge_rating_helper(match_df,player_df,col,newname):
    '''
    This is a helper function that merges in the overall player ratings into the match dataframe.

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
    try: 
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
    except:
        logging.error("Error occurred - check dataframe has all necessary columns")
        return None

def ewma_score(match_df,a=.5,p=4):
    '''
    This function creates an exponentially weighted moving average of the teams record over the season.

    :param match_df: Dataframe of matches
    :param a: Float indicating the rate of decay for the moving average. Must be >0 and <=1
    :param p: Int indicating how many periods to skip at beginning of season. Default is 4
    '''
    home_teams = match_df[['date','season','home_team_api_id','outcome']].rename(columns={'home_team_api_id':'team_id'})
    home_teams['shift_ewma'] = 0
    home_teams.loc[home_teams.outcome=='Home','shift_ewma']=1
    home_teams.loc[home_teams.outcome=='Away','shift_ewma']=-1
    away_teams = match_df[['date','season','away_team_api_id','outcome']].rename(columns={'away_team_api_id':'team_id'})
    away_teams['shift_ewma'] = 0
    away_teams.loc[away_teams.outcome=='Home','shift_ewma']=-1
    away_teams.loc[away_teams.outcome=='Away','shift_ewma']=1
    all_teams = home_teams.append(away_teams).sort_values(by=['team_id','date'])
    all_teams = all_teams.drop(columns='outcome')
    all_teams['ewma'] = all_teams.groupby('team_id')['shift_ewma'].transform(lambda x: x.shift(1))
    all_teams = all_teams.fillna(0)
    all_teams['ewma'] = all_teams.groupby(['team_id'])['ewma'].transform(lambda v: v.ewm(alpha=a,min_periods=p).mean())
    all_teams = all_teams.fillna(0)
    all_teams = all_teams.drop(columns=['shift_ewma'])
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

def merge_ratings(match_df,player_attr):
    '''
    Function calculates the player ratings for each player by week, and merges with the match dataframe.

    @param match_df:    Dataframe of match results with each player.
    @param player_attr: Dataframe of FIFA player attributes over time.
    @return:            Match Dataframe with the player ratings included.
    '''
    player_vars = [name+str(i) for name in ('home_player_','away_player_') for i in range(1,12)] + ['date']
    player_list = match_df.drop(match_df.columns.difference(player_vars), axis=1)
    player_list = player_list.melt(id_vars = 'date',var_name='player',value_name='player_id')
    player_list = player_list.drop(labels='player',axis=1)

    attributes = player_attr.drop(player_attr.columns.difference(['date','player_api_id','overall_rating']),axis=1)
    attributes.rename(columns={'player_api_id':'player_id'},inplace=True)
    player_list = player_list.append(attributes,ignore_index=True,sort=False).drop_duplicates()
    player_list = player_list.sort_values(by=['player_id','date'])
    player_list = player_list.loc[player_list.player_id.isna()==False]
    player_list['overall_rating'] = player_list.groupby('player_id')['overall_rating'].transform(lambda v: v.ffill())

    ##Some players have multiple ratings on the same day - take average
    player_list = pd.DataFrame(player_list.groupby(['player_id','date'])['overall_rating'].mean()).reset_index()

    for i in range(1,12):
        for name in ('home_player_','away_player_'):
            col = name+str(i)
            if name=='home_player_':
                newname = 'hp'+str(i)
            else:
                newname = 'ap'+str(i)
            match_df = merge_rating_helper(match_df,player_list,col,newname)
    return match_df

def run_all_feat_eng(data_location,final_location,leagues,droplabels):
    '''
    Function performs all of the data cleaning and feature engineering using the above functions and saves out a clean dataset

    @param data_location:  Filepath to the raw fifa database
    @param final_location: Filepath to save the final CSV
    @param leagues:        List of leagues to be included and analyzed
    @param droplabels:     List of columns to be dropped from the match dataframe.
    @return:               None
    '''
    conn = sqlite3.connect(data_location)
    cur = conn.cursor()
    match = get_table(cur,'Match')
    player_attributes = get_table(cur,'Player_Attributes')

    ##Keep only the relevant leagues
    match = match.loc[match.league_id.isin(leagues)]

    ##Drop unused variables
    match = match.drop(labels=droplabels,axis=1)

    ##Create outcome feature
    match['outcome'] = match.apply(winner,axis=1)

    ##Merge fifa ratings
    match = merge_ratings(match,player_attributes)

    ## Calculate average rating scores
    match = eng_ratings(match)

    ## Calculate ewma 
    match = ewma_score(match)

    match.to_csv(final_location,index=False)
