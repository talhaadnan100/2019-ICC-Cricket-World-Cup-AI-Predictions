"""
This script uses the scraping functions from scrapper.py to aggregate
One-Day International (ODI) matche details from ESPN CricInfo.

Created by: Talha Siddiqui

Dependencies: argparse, pandas and bs4

Usage: python scripts/data.py 1971 2019
"""

import argparse
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
        matches: (pandas.Dataframe) High-level summary of ODI matches include teams, ground, winner and margin
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
                        details = get_player_details(BeautifulSoup(html, "html.parser"), str(match_date))
                        player_details.append(details)
                    except KeyError:
                        html = get_webpage(link)
                        details = get_player_details(html, str(match_date))
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

    ## Handle Missing Values    
    # Bowling Average: Lower the better, so missing values ought to be the worst a.k.a highest
    for c in [c for c in matches_scorecard.columns if c[-8:]=="bowl_ave"]:
        highest = matches_scorecard[c].max()
        matches_scorecard[c].replace(0,highest, inplace=True)
        matches_scorecard[c].fillna(highest, inplace=True)

    # Bowling Economy: Lower the better, so missing values ought to be the worst a.k.a highest
    for c in [c for c in matches_scorecard.columns if c[-9:]=="bowl_econ"]:
        highest = matches_scorecard[c].max()
        matches_scorecard[c].replace(0,highest, inplace=True)
        matches_scorecard[c].fillna(highest, inplace=True)

    # Bowling Strike Rate: Lower the better, so missing values ought to be the worst a.k.a highest
    for c in [c for c in matches_scorecard.columns if c[-7:]=="bowl_sr"]:
        highest = matches_scorecard[c].max()
        matches_scorecard[c].replace(0,highest, inplace=True)
        matches_scorecard[c].fillna(highest, inplace=True)
        
    # Batting Average: Higher the better, so missing values ought to be the worst a.k.a lowest after 0
    for c in [c for c in matches_scorecard.columns if c[-7:]=="bat_ave"]:
        lowest = matches_scorecard[matches_scorecard[c]>0][c].min()
        matches_scorecard[c].replace(0,lowest, inplace=True)
        matches_scorecard[c].fillna(lowest, inplace=True)

    # Batting Strike Rate: Higher the better, so missing values ought to be the worst a.k.a lowest after 0
    for c in [c for c in matches_scorecard.columns if c[-6:]=="bat_sr"]:
        lowest = matches_scorecard[matches_scorecard[c]>0][c].min()
        matches_scorecard[c].replace(0,lowest, inplace=True)
        matches_scorecard[c].fillna(lowest, inplace=True)
        
    # Age on day of match: Average seems to be the reasonable choice
    for c in [c for c in matches_scorecard.columns if c[-3:]=="age"]:
        avg = matches_scorecard[c].mean()
        matches_scorecard[c].replace(0,avg, inplace=True)
        matches_scorecard[c].fillna(avg, inplace=True)
    
    if save_to_file == True:
        matches_scorecard.to_csv("../data/matches_scorecard_player_details.csv", index=False)
    
    return matches_scorecard

def player_details_dataframe(data, save_to_file = True):
    """
    Using the complete aggregated data for all ODIs, this script compiles each player's information
    who played on behalf of a certain team.

    Keywords:
        data (pandas.Dataframe) Complete table of player details for all played ODIs
        save_to_file: (bool) Keeping a record of generated DataFrame as a CSV

    Return
        matches_scorecard: (pandas.Dataframe) Compiled table of each ODI teams' players with their attributes and stats
    """
    complete = []
    for team in range(1,3):
        for player in range(1,13):
            column = 'team_' + str(team) + '_player_' + str(player)
            # Loop through the data in reverse order to get the most recent players first
            for index, row in data[::-1].iterrows():
                player_details = []
                player_details.append(row['team_' + str(team)])
                for detail in ['_name', '_url', '_age', '_style', '_batting_style', '_bowling_style', '_bat_ave', '_bat_sr', '_bowl_ave', '_bowl_econ', '_bowl_sr']:
                    player_details.append(row[column+detail])            
                complete.append(player_details)
    player_details_dataframe = pd.DataFrame(complete, columns=['team', 'name', 'url','avg_age','style', 'batting_style', 'bowling_style', 'bat_ave', 'bat_sr', 'bowl_ave', 'bowl_econ', 'bowl_sr']).sort_values('team')
    player_details_dataframe = player_details_dataframe.groupby(['team', 'name','url', 'style', 'batting_style', 'bowling_style'], sort=False).mean().reset_index()
    
    if save_to_file == True:
        player_details_dataframe.to_csv("../data/complete_player_details.csv", index=False)

    return player_details_dataframe

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_year')
    parser.add_argument('end_year')
    args = parser.parse_args()

    # Initial set of ODI matches played in the desired years
    matches = initiate_match_results_dataframe(start_year=args.start_year, end_year=args.end_year, save_to_file=True)

    # For the ODI scraped above, extending details with player names and URLs
    matches_scorecard = extent_scorecard_dataframe(matches, save_to_file=True)

    # Aggregating each player's information for each ODI match
    matches_scorecard_player_details = complete_scraped_dataframe(matches_scorecard, save_to_file=True)

    # Compiling a record of each teams' players
    player_details_dataframe(matches_scorecard_player_details, save_to_file=True)

if __name__ == "__main__":
    main()