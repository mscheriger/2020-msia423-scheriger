import pytest
import pandas as pd
from src.feat_eng import get_table, winner, eng_ratings, ewma_score, merge_ratings
import sqlite3

def test_get_table_good():
    ##Good path for get_table function
    ##Verify database is in correct path, otherwise test fails

    path = 'data/fifa_s3.db'
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    df = get_table(cur,'Country')
    assert df.shape==(11,2)

def test_get_table_bad():
    ##Bad path for get_table function

    path = 'data/fifa_s3.db'
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    df = get_table(cur,'Broken')
    assert df==None

def test_winner():
    data = [[0,0],[1,2],[2,1]]
    df = pd.DataFrame(data,columns=['home_team_goal','away_team_goal'])
    outcome = df.apply(winner,axis=1)
    assert all((outcome[0]=="Draw",outcome[1]=="Away",outcome[2]=="Home"))

def test_eng_ratings_good():
    data = [[6,9,8,7,9,8,7,8,8,7,9,8,8,7,6,8,7,6,7,7,6,8]]
    df = pd.DataFrame(data,columns=['hp1','hp2','hp3','hp4','hp5','hp6','hp7','hp8','hp9','hp10','hp11','ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8','ap9','ap10','ap11'])
    final = eng_ratings(df)
    assert final.home_overall_rating[0]==86/11
    assert final.away_overall_rating[0]==78/11
    assert final.home_def_rating[0]==33/4
    assert final.away_def_rating[0]==29/4
    assert final.home_mid_rating[0]==23/3
    assert final.away_mid_rating[0]==20/3
    assert final.home_off_rating[0]==8
    assert final.away_off_rating[0]==7

def test_eng_ratings_bad():
    data = [[6,9,8,7,9,8,7,8,8,7,9,8,8,7,6,8,7,6,7,7,6]]
    df = pd.DataFrame(data,columns=['hp1','hp2','hp3','hp4','hp5','hp6','hp7','hp8','hp9','hp10','hp11','ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8','ap9','ap10'])
    final = eng_ratings(df)
    assert final==None

def test_ewma_score():
    data = [["2010-01-01","1",1,2,"Draw"],["2010-01-08","1",1,2,"Home"],["2010-01-15","1",1,2,"Home"],["2010-01-22","1",1,2,"Away"],["2010-01-29","1",1,2,"Away"]]
    df = pd.DataFrame(data,columns=["date","season","home_team_api_id","away_team_api_id","outcome"])
    final = ewma_score(df)
    assert abs(final.home_ewma[4]-(-0.129032))<.0001
    assert abs(final.away_ewma[4]-0.129032)<.0001

def test_merge_ratings():
    path = 'data/fifa_s3.db'
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    matches = get_table(cur,'Match')
    matches = matches.loc[matches.league_id==1729]
    players = get_table(cur,'Player_Attributes')
    df = merge_ratings(matches,players)
    assert df.ap11[0]==83
    assert df.hp1[2]==78
    assert df.ap5[4]==73
