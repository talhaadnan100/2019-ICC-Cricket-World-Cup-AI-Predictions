"""
This script uses the scraping functions from scrapper.py to aggregate
One-Day International (ODI) matche details from ESPN CricInfo.

Created by: Talha Siddiqui
"""

import pandas as pd
from bs4 import BeautifulSoup

from scrapper import get_webpage, get_odi_match_results, get_scorecard_details, get_player_details

def initiate_match_results_dataframe(start_year=1971, end_year=2019, save_to_file=False):
    """
    Initializes a dataframe that is extracted from the scraped match results webpages
    between the specified start year and end year excluding matches with no result

    Keywords:
        start_year: (int) ODI matches to scrape from specified year
        end_year: (int) ODI matches to scrape to specified year
        save_to_file: (bool) Keeping a record of generated DataFrame as a CSV

    Return
        matches: (pandas.Dataframe) 
    """

    matches = pd.DataFrame(get_odi_match_results(get_webpage('http://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id='+ str(start_year) +';type=year')))
    for year in list(range(start_year+1, end_year+1)):
        soup = get_webpage('http://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id='+ str(year) +';type=year')
        matches = matches.append(get_odi_match_results(soup))
    matches = matches[matches['winner'] != 'no result']
    matches = matches.reset_index(drop=True)

    if save_to_file == True:
        matches.to_csv("../data/match_results.csv", index=False)

    return matches

def extent_scorecard_dataframe(matches, save_to_file=False):
    """
    Adding relevant scorecard details to record of ODI matches (must contain scorecard_url)

    Keywords:
        matches (pandas.Dataframe) Table of match results containing scorecard URL
        save_to_file: (bool) Keeping a record of generated DataFrame as a CSV

    Return
        matches_scorecard: (pandas.Dataframe) All player and match information DataFrame
    """
    # Utilizing the archive
    archive = pd.read_csv("../data/archive/archive-matches.csv", index_col=0)

    scorecard = []
    for link in matches['scorecard_url']:
        try:
            html = archive.loc[link][0]
            scorecard.append(get_scorecard_details(BeautifulSoup(html, "html.parser")))
        except KeyError:
            html = get_webpage(link)
            scorecard.append(get_scorecard_details(html))

    scorecard_df = pd.DataFrame(scorecard)
    matches_scorecard = pd.concat([matches, scorecard_df], axis=1, sort=False)
    matches_scorecard.columns = ['team1','team2','winner','margin','ground','ground_url','match_date','scorecard','scorecard_url',
                                'world_cup','attendance', 'team_1','team_1_player_1_name','team_1_player_1_url','team_1_player_2_name',
                                'team_1_player_2_url','team_1_player_3_name','team_1_player_3_url','team_1_player_4_name',
                                'team_1_player_4_url','team_1_player_5_name','team_1_player_5_url','team_1_player_6_name',
                                'team_1_player_6_url','team_1_player_7_name','team_1_player_7_url','team_1_player_8_name',
                                'team_1_player_8_url','team_1_player_9_name','team_1_player_9_url','team_1_player_10_name',
                                'team_1_player_10_url','team_1_player_11_name','team_1_player_11_url','team_1_player_12_name',
                                'team_1_player_12_url','team_2','team_2_player_1_name','team_2_player_1_url','team_2_player_2_name',
                                'team_2_player_2_url','team_2_player_3_name','team_2_player_3_url','team_2_player_4_name',
                                'team_2_player_4_url','team_2_player_5_name','team_2_player_5_url','team_2_player_6_name',
                                'team_2_player_6_url','team_2_player_7_name','team_2_player_7_url','team_2_player_8_name',
                                'team_2_player_8_url','team_2_player_9_name','team_2_player_9_url','team_2_player_10_name',
                                'team_2_player_10_url','team_2_player_11_name','team_2_player_11_url','team_2_player_12_name',
                                'team_2_player_12_url']
    if save_to_file == True:
        matches_scorecard.to_csv("../data/matches_scorecard_details.csv", index=False)

    return matches_scorecard

def complete_scraped_dataframe(matches_scorecard, save_to_file=False):
    """
    Adding player statistics (batting averages, batting strike rate, bowling averages, bowling strike rate and bowling economy) 
    to matches scorecard DataFrame containing list of players and their corresponding URLs

    Keywords:
        matches_scorecard (pandas.Dataframe) Table of match results containing scorecard information i.e. player URLs
        save_to_file: (bool) Keeping a record of generated DataFrame as a CSV

    Return
        matches_scorecard: (pandas.Dataframe) Complete table of player details for all played ODIs
    """
    # Utilizing the archive
    archive = pd.read_csv('../data/archive/archive-players.csv', index_col=0)

    # Looping through all the players from both teams to extract that statistics
    for team in range(1,3):
        for player in range(1,13):
            column = 'team_' + str(team) + '_player_' + str(player) + '_url'
            player_details = []
            
            # Looping through row by row of the matches scorecard
            for index, row in matches_scorecard.iterrows():
                link = row[column]
                match_date = row['match_date']
                if type(link) != str:
                    player_details.append([None,None,None,None,None,None,None,None,None])
                else:
                    # The one-off case where a URL is incomplete
                    if len(link)==29:
                        link = 'http://www.espncricinfo.com'+link

                    # Getting the figures from the player's webpage
                    try:
                        html = archive.loc[link][0]
                        details = get_player_details(BeautifulSoup(html, "html.parser"), match_date)
                        player_details.append(details)
                    except KeyError:
                        html = get_webpage(link)
                        details = get_player_details(html, match_date)
                        player_details.append(details)
                    except:
                        player_details.append([None,None,None,None,None,None,None,None,None])                        
            
            # Create a DataFrame from all the scraped data from this one player
            prefix = column[:-3]
            player_detail_columns = [prefix + 'age', prefix + 'style', prefix + 'batting_style', 
                                    prefix + 'bowling_style', prefix + 'bat_ave', prefix + 'bat_sr', 
                                    prefix + 'bowl_ave', prefix + 'bowl_econ', prefix + 'bowl_sr']
            player_details_df = pd.DataFrame(player_details, columns=player_detail_columns)
            player_details_df = player_details_df.reset_index(drop=True)

            # Ensure the columns that are about to be appended to the DataFrame are consistent in length
            if len(matches_scorecard)==len(player_details_df):
                matches_scorecard = pd.concat([matches_scorecard, player_details_df], axis=1, sort=False)
            else:
                print('Dataframe and player details mismatch for:', column)

    if save_to_file == True:
        matches_scorecard.to_csv("../data/matches_scorecard_player_details.csv", index=False)
    
    return matches_scorecard

