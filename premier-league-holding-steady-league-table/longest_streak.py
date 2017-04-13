'''This module takes in English Premier League results data and calculates
longest amount of time teams stay in the same position
'''

import math
from datetime import timedelta
import numpy as np
import pandas as pd
import requests


def download_files(season, division):
    url = f'http://www.football-data.co.uk/mmz4281/{season}/{division}.csv'
    r = requests.get(url, stream=True)

    with open(f'epl/data/{division}/{season}.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian

## http://stackoverflow.com/questions/19914937/applying-function-with-multiple-arguments-to-create-a-new-pandas-column
def get_result(x, y):
    if x == y:
        return 'D'
    elif x > y:
        return 'W'
    else:
        return 'L'

points_map = {
    'W': 3,
    'D': 1,
    'L': 0
}

def standings(frame, result_col, goals_col, goals_opp_col, points_col):
    """This function takes in a DataFrame and strings identifying fields
    to calculate the league table.
    
    Making it generalized will allow us to calculate league tables for
    First Half Goals only. Second Half Goals only.
    """
    record = {}
    
    record['Played'] = np.size(frame[result_col])
    record['Won'] = np.sum(frame[result_col] == 'W')
    record['Drawn'] = np.sum(frame[result_col] == 'D')
    record['Lost'] = np.sum(frame[result_col] == 'L')
    record['GF'] = np.sum(frame[goals_col])
    record['GA'] = np.sum(frame[goals_opp_col])
    record['GD'] = record['GF'] - record['GA']
    record['Points'] = np.sum(frame[points_col])
    
    return pd.Series(record, index=['Played', 'Won', 'Drawn', 'Lost', 'GF', 'GA', 'GD', "Points"])

def rank_teams(league_table, team_list):
    """Return a Series of ranked teams, including those who have yet to play
    
    Args:
        * league_table - League Table DataFrame
        * team_list - List of all teams in league
    """
    
    # sort by tiebraker and rank
    team_rank = (league_table
                     .apply(lambda row: (row['Points'], row['GD'], row['GF']), axis=1)
                     .rank(method='min', ascending=False)
                     .astype(int))
    
    # if not all teams are ranked (i.e. some of them might have not have played yet)
    if team_rank.size < len(team_list):
        # get all teams that need to be added to the table
        ranked_teams = team_rank.index.values
        teams_to_add = {team for team in team_list if team not in ranked_teams}  
        
        # position to remaining teams
        rank_to_assign = team_rank.size + 1
        
        # add teams that haven't played a game to rankings
        team_pos = {}
        for team in teams_to_add:
            team_pos[team] = rank_to_assign
        team_rank = team_rank.append(pd.Series(data=team_pos))
    
    return team_rank

def get_historical_ranks(team_results, all_dates):
    """Gets position of team across the entire season

    Args:
        * team_results - DataFrame of results for each team
        * all_dates - list of dates we want to calculate ranks across
    """

    rank_history = []
    # calculate ranks after each day there is a game
    for day in all_dates:
        # get results up to current day
        dailyresults_byteam = (team_results[team_results['Date'] <= day]
                                .groupby(['Team']))
        
        # create league table with ranking
        # premier league ranking goes: Points, GD, GF
        league_table = (dailyresults_byteam
                            .apply(standings, 'Result', 'Goals', 'Goals_Opp', 'Points')
                            .sort_values(by=['Points', 'GD', 'GF'], ascending=False))
        team_rank = rank_teams(league_table, all_teams)
        
        rank_history.append(team_rank)
            
    # create historical ranking dataframe
    rank_history = (pd.DataFrame
                        .from_records(rank_history, index=all_dates))

    # Reindex and include all dates
    idx = pd.date_range(rank_history.index.min(), rank_history.index.max())
    rank_history = rank_history.reindex(idx, method='ffill')

    return rank_history


## http://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


if __name__ == '__main__':

    curr_year_only = False
    start_season = 1993
    curr_season = 2016
    division = 'E0'

    # if we only want to update current year data
    if curr_year_only:
        start_season = 2016

    # go thru each season
    for year in range(start_season, curr_season+1):
        season = str(year)[-2:] + str(year+1)[-2:]

        # download_files(
        #     season=season,
        #     division='E0')

        results = pd.read_csv(
            f'epl/data/{division}/{season}.csv',
            usecols=[x for x in range(7)],
            parse_dates=['Date'],
            dayfirst=True)

        # convert home/away data to game log data (each team has a row per game)
        results['H'] = results['HomeTeam']
        results['A'] = results['AwayTeam']

        team_results = pd.melt(
            results, 
            id_vars=['Div', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTHG', 'HTAG', 'HTR', 'Referee'], 
            value_vars = ['H', 'A'],
            var_name='Home/Away', value_name='Team')

        team_results['Opponent'] = \
            np.where(team_results['Team'] == team_results['HomeTeam'], team_results['AwayTeam'], team_results['HomeTeam'])

        ## add additional fields to dataframe
        # full time goals
        team_results['Goals'] = \
            np.where(team_results['Team'] == team_results['HomeTeam'], team_results['FTHG'], team_results['FTAG'])
        team_results['Goals_Opp'] = \
            np.where(team_results['Team'] != team_results['HomeTeam'], team_results['FTHG'], team_results['FTAG'])
        team_results['Result'] = np.vectorize(get_result)(team_results['Goals'], team_results['Goals_Opp'])
        team_results['Points'] = team_results['Result'].map(points_map)

        # Drop unnecessary columns and sort by date
        team_results = \
            team_results.drop(['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'], axis=1)

        # get all days and teams we need to rank
        all_dates = team_results['Date'].unique()
        all_teams = np.sort(team_results['Team'].unique())

        # get ranking across all days in the season
        rank_history = get_historical_ranks(team_results, all_dates)

        # get longest conseuctive ranks for each team across the season
        ## http://stackoverflow.com/questions/14358567/finding-consecutive-segments-in-a-pandas-data-frame
        print()
        print(f'{season}')
        for team in all_teams:
            df = rank_history[team].to_frame()
            df.columns = ['A']
            df['block'] = (df.A.shift(1) != df.A).astype(int).cumsum()
            streak_lengths = df.reset_index().groupby(['A','block'])['index'].apply(np.size)
            
            pos = streak_lengths.argmax()[0]
            max_length = streak_lengths.max()

            # only show longer than united in 6th
            if max_length >= 104:
                print(f'{team} was {ordinal(pos)} for {max_length} days')  # f-string! =)
