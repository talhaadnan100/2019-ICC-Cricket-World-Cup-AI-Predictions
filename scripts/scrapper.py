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
        webpage = BeautifulSoup(html_request.text, features="lxml")
        attempts = 1

        # Retry upto 5 times to reread the page
        while attempts < 5 and 'Page error' in webpage.text:
            # Take a deep breath, and try again
            time.sleep(attempts)
            html_request = requests.get(url)
            webpage = BeautifulSoup(html_request.text, features="lxml")
            attempts += 1
        
        if 'Page error' in webpage.text:
            print('Cannot process',url)
            print('Keep bumping into Page error, buddy! ¯\_(ツ)_/¯') 
        else:
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
        details: (list) comprising of World Cup Match (boolean), Attendence (int), players' names (str) and urls(str)
    """

    details = []

    # World cup match or not?
    WC = 'World Cup' in soup.find('div', {"class":"cscore_info-overview"}).text
    details.append(WC)

    # Getting attendence
    attendance = None
    for div in soup.find_all('div', {"class": "accordion-content collapse in"}):
        for li in div.find_all('li'):        
            if 'Attendance' in li.text:
                # Taking out match revenue detailed added to attendance with paranthesis 
                if "(" in li.text:
                    attendance = int(''.join(re.findall('\:\s(.*)\s', li.text)).replace(',',''))
                else:
                    attendance = int(''.join(re.findall('\d+', li.text)))
    details.append(attendance)

    # Getting players
    for li in soup.find_all('li', {"class": "accordion-item"}):
        try:
            team = None
            team = li.find('h2').text.replace(' Innings','')
        except AttributeError:
            continue
        details.append(team)
        for div in li.find_all('div', {"class":"scorecard-section batsmen"}):
            for a in div.find_all('a'):
                if a["href"][-4:]=='html':
                    name = a.text.replace(" †","").replace(" (c)","")
                    details.append(name)
                    details.append(a['href'])


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