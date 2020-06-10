import pytest
import pandas as pd
from src.clean_predictions import best_line, bet_on_profit

def test_best_line():
    data = [[1,3,2,-1]]
    df = pd.DataFrame(data,columns=['a','b','c','d'])
    final = df.apply(best_line,axis=1,columns=['a','b','c','d'])
    assert final[0]==3

def test_bet_on_profit():
    data = [['Team A','Team B',2,1/3,3,1/3,4,1/3,"Draw","Draw"]]
    df = pd.DataFrame(data,columns=['home_team_name','away_team_name','home_line','home_prob','away_line','away_prob','draw_line','draw_prob','team_outcome',"outcome"])
    bets = df.apply(bet_on_profit,axis=1)
    assert bets[0][0]=="Draw"
    assert abs(bets[0][1]-1/3)<.0001
    assert bets[0][2]==3
