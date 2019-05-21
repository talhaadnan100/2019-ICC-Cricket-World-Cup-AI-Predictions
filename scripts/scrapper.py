import pandas as pd
import re
import time
import datetime
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

    # Distributing archive for efficient retrieval
    if 'player' in url:
        archive = pd.read_csv('../data/archive/archive-players.csv', index_col=0)
    elif 'ground' in url:
        archive = pd.read_csv('../data/archive/archive-grounds.csv', index_col=0)
    else:
        archive = pd.read_csv("../data/archive/archive-matches.csv", index_col=0)

    try:
        # Explore archive first to avoid excessively hitting the server
        html = archive.loc[url][0]
        return BeautifulSoup(html, "html.parser")
    except KeyError:
        # Be polite to the webserver
        time.sleep(.5)

        # Get the webpage from the Website
        html_request = requests.get(url)
        webpage = BeautifulSoup(html_request.text, features="lxml")
        attempts = 1

        # Retry upto 5 times to reread the page
        while attempts < 5 and 'Page error' in webpage.text:
            # Take a deep breath, and try again. Giving more rest to the server at each attempt
            time.sleep(attempts)
            html_request = requests.get(url)
            webpage = BeautifulSoup(html_request.text, features="lxml")
            attempts += 1
        
        # Archive scrapped webpage for future use, but exclude Page Error or 2019 match results
        if 'Page error' in webpage.text:
            print('Cannot process',url)
            print('Keep bumping into Page error, buddy! ¯\_(ツ)_/¯')
        elif 'match_results.html?class=2;id=2019;type=year' in url:
            print('FYI: 2019 match results will not be archived, because updates are expected.')
            return webpage
        else:
            add = pd.DataFrame([[url,webpage]],columns=['url','html'])        
            add.set_index('url', inplace=True)
            if 'player' in url:
                add.to_csv('../data/archive/archive-players.csv', mode='a', header=False)
            elif 'ground' in url:
                add.to_csv('../data/archive/archive-grounds.csv', mode='a', header=False)
            else:
                add.to_csv('../data/archive/archive-matches.csv', mode='a', header=False)

            return webpage
        

def initiate_match_results_dataframe(start_year=1971, end_year=2019, save_to_file=False):
    """
    Initializes a dataframe that is extracted from the scraped match results webpages
    between the specified start year and end year

    Keywords:
        start_year: (int) ODI matches to scrape from specified year
        end_year: (int) ODI matches to scrape to specified year
        save_to_file: (bool) 

    Return
        matches: (pandas.Dataframe) 
    """

    matches = pd.DataFrame(get_odi_match_results(get_webpage('http://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id='+ str(start_year) +';type=year')))
    for year in list(range(start_year+1, end_year)):
        soup = get_webpage('http://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id='+ str(year) +';type=year')
        matches = matches.append(get_odi_match_results(soup))
    matches = matches.reset_index(drop=True)

    if save_to_file == True:
        matches.to_csv("../data/match_results.csv", index=False)

    return matches

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
                    attendance = int(''.join(re.findall('\s(\d.*)\s\(', li.text)).replace(',','').replace(' ',''))
                else:
                    attendance = int(''.join(re.findall('\d+', li.text)))
    details.append(attendance)

    # Getting players
    for li in soup.find_all('li', {"class": "accordion-item"}):
        players = []
        try:
            team = None
            team = li.find('h2').text.replace(' Innings','')
        except AttributeError:
            continue
        players.append(team)
        for div in li.find_all('div', {"class":"scorecard-section batsmen"}):
            for a in div.find_all('a'):
                try: 
                    if ('player' in a["href"]) & (a["href"][-4:]=='html'):
                        name = a.text.replace(" †","").replace(" (c)","")
                        players.append(name)
                        players.append(a['href'])
                except:
                    continue
        while len(players) < 25: players.append(None)
        details = details + players


    return details

def get_player_details(soup, match_date):
    """
    Given a BeautifulSoup object of an ODI cricket player, get the relevant batting and bowling details including age on date of the match in days.

    Keyword:
        soup: (BeautifulSoup) ODI cricket player
        match_date: (str) ODI cricket match date

    Return:
        details: (list) batting and bowling details including Date of Birth.
    """

    # Standardize match_date to datetime for difference calculation later
    if len(match_date) == 19: md = datetime.datetime.strptime(match_date, "%Y-%m-%d %H:%M:%S")
    if len(match_date) == 10: md = datetime.datetime.strptime(match_date, "%Y-%m-%d")

    age = None
    style = None
    batting_style = None
    bowling_style = None
    
    for p in soup.find_all('p', {"class":"ciPlayerinformationtxt"}):
        if p.text[:4] == 'Born':
            # get player age
            dob = pd.to_datetime(re.search('\w{3,9}?\s\d{1,2}?,\s\d{4}?', p.text).group(0))
            age = (md - dob).days
        if p.text[:4] == 'Play':
            # Get player style
            style = p.find('span').text
        if p.text[:4] == 'Batt':
            # Get batting style
            batting_style = p.find('span').text
        if p.text[:4] == 'Bowl':
            # Get bowling style
            bowling_style = p.find('span').text
    
    bat = []
    bowl = []
    for obs, table in enumerate(soup.find_all('table', {"class":"engineTable"})):
        if obs == 0: # Batting averages
            for tr in table.find_all('tr', {"class":"head"}):
                th = tr.find_all('th')
                head = [tr.text for tr in th]
            for tr in table.find_all('tr'):
                td = tr.find_all('td')
                row = [tr.text for tr in td]
                bat.append(row)
            # Consolidate HTML table to Pandas Dataframe
            batting = pd.DataFrame(bat, columns=head)
            batting.set_index("",drop=True,inplace=True)
            batting.dropna(inplace=True)
            batting.replace(to_replace='-', value=0, inplace=True)

        elif obs == 1: # Bowling averages
            for tr in table.find_all('tr', {"class":"head"}):
                th = tr.find_all('th')
                head = [tr.text for tr in th]
            for tr in table.find_all('tr'):
                td = tr.find_all('td')
                row = [tr.text for tr in td]
                bowl.append(row)
            # Consolidate HTML table to Pandas Dataframe
            bowling = pd.DataFrame(bowl, columns=head)
            bowling.set_index("",drop=True,inplace=True)
            bowling.dropna(inplace=True)
            bowling.replace(to_replace='-', value=0, inplace=True)
                
    bat_ave = float(batting.loc['ODIs','Ave']) 
    bat_sr = float(batting.loc['ODIs','SR'])
    bowl_ave = float(bowling.loc['ODIs','Ave'])
    bowl_econ = float(bowling.loc['ODIs','Econ'])
    bowl_sr = float(bowling.loc['ODIs','SR'])
    
    details = [age, style, batting_style, bowling_style, bat_ave, bat_sr, bowl_ave, bowl_econ, bowl_sr]


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