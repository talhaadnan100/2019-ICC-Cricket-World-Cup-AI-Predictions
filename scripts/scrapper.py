import pandas as pd
import re
import time
import requests
from bs4 import BeautifulSoup

def get_webpage(url):
    """
    Given a URL, return a webpage HTML. If the webpage has been scraped before return archived text, otherwise politely scrape it.

    Keywords:
        url: (str) url of webpage to be scraped

    Return
        webpage: (BeautifulSoup) html parsed text from a webpage
    """
    
    archive = pd.read_csv("../data/archive.csv", index_col=0)

    try:
        # Explore archive first to avoid excessively hitting the server
        html = archive.loc[url][0]
        return BeautifulSoup(html, "html.parser")
    except KeyError:
        # Get the webpage from the Website
        html_request = requests.get(url)
        webpage = BeautifulSoup(html_request.text)

        # Archive for future use
        add = pd.DataFrame([[url,webpage]],columns=['url','html'])        
        add.set_index('url', inplace=True)
        add.to_csv('../data/archive.csv', mode='a', header=False)

        # Be polite to the webserver
        time.sleep(.5)

        return webpage

def get_odi_match_results(soup):
    """
    Given a BeautifulSoup object of ODI match results, get a dataframe of teams, winner, margin, ground and scorecard.

    Keyword:
        soup: (BeautifulSoup) ODI match results

    Return:
        matches: (Dataframe) With teams, winner, margin, ground, ground URL, match date, scorecard and scorecard URL.
    """

    l = []
    for table in soup.find_all('tbody'):
        for tr in table.find_all('tr'):
            td = tr.find_all('td')
            row = []
            for cell in td:
                row.append(cell.text)
                # Obtain Ground and Scorecard URLs
                try:
                    if 'ground' in cell.find('a')['href']: row.append('http://stats.espncricinfo.com' + cell.find('a')['href']) 
                    if 'match' in cell.find('a')['href']: row.append('http://stats.espncricinfo.com' +cell.find('a')['href']) 
                except TypeError:
                    continue
            l.append(row)
    matches = pd.DataFrame(l, columns=['team_1','team_2','winner','margin','ground','ground_url','match_date','scorecard','scorecard_url'])

    # For any ODI's that took more than a day to finish,
    # consider only the first day as the match date
    matches = matches.replace("\-.*,","", regex=True)

    # Convert Match Date strings to datetime objects for easy manipulation
    matches['match_date'] = pd.to_datetime(matches['match_date'])

    return matches

def get_scorecard_details(soup):
    """
    Given a BeautifulSoup object of ODI match scorecard, get all the relevant information including players in a list format

    Keyword:
        soup: (BeautifulSoup) ODI match scorecard

    Return:
        details: (list) Match type, players, etc.
    """

    details = []


    return details

def get_player_details(soup):
    """
    Given a BeautifulSoup object of an ODI cricket player, get the relevant batting and bowling details including Date of Birth.

    Keyword:
        soup: (BeautifulSoup) ODI cricket player

    Return:
        details: (list) batting and bowling details including Date of Birth.
    """

    details = []


    return details

def get_ground_details(soup):
    """
    Given a BeautifulSoup object of a cricket ground, get the relevant city, country, year established, and pitch type.

    Keyword:
        soup: (BeautifulSoup) cricket ground

    Return:
        details: (list) city, country, year established, and pitch type.
    """

    details = []


    return details