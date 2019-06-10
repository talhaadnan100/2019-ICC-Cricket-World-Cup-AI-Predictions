### _[Work in Progress](https://github.com/talhaadnan100/2019-ICC-Cricket-World-Cup-AI-Predictions/issues/1)_

## 2019 ICC Cricket World Cup AI Predictions

Using AI to predict the outcome of the 2019 ICC Cricket World Cup :cricket:

### Motivation

Cricket has always been a big part of my life since. In particular, the international one-day format is always been my favorite. Even after I moved to North America in my late teens, I would wake up early morning on weekends to watch the matches live.

As I am wrapping up my degree in [Master of Data Science](https://masterdatascience.ubc.ca/) from [University of British Columbia](http://www.ubc.ca/) in Vancouver, BC, Canada, I could think of a better pet-project to put some of my data skills to test than predicting the winner of the 2019 ICC Cricket World Cup.

### Data

The primary source of data for this project is [ESPNcricinfo.com](ESPNcricinfo.com). The website is truly unparalleled in terms of the wealth of statistics it possesses. Scripts will scrape one-day international matches' and players' details.

The complete data is present in the following files:

- `match_results.csv`: High-level summary of ODI matches include teams, ground, winner and margin
- `matches_scorecard_details.csv`: All player names and URLs, and misc. match information such as attendance
- `matches_scorecard_player_details.csv`: Complete table of player details including style, batting and bowling figures
- `complete_player_details.csv`: Compiled table of ODI teams' players with their attributes and stats

To recreate the data files, run the script with your desired start and end years. For instance:

Usage: `python scripts/data.py 1971 2019`

### Predictive Modeling

A baseline [scikit learn](https://scikit-learn.org/stable/index.html) Logistic Regression and/or Decision Tree Classifier will serve as a starting point. Then, more advanced machine learning models will be introduced.

### Dependencies

Python version 3.6.8 and the following python packages:
- pandas (version 0.24.2)
- requests (version 2.21.0)
- bs4 (version 4.7.1)
- re (version 2.2.1)
- sklearn (version 0.20.1)
- matplotlib (version 3.0.3)
- argparse (version 1.1)

### Attribution

- Data acquired from [ESPNcricinfo.com](ESPNcricinfo.com)
- Preliminary inspiration from [jaykay12's CricAI](https://github.com/jaykay12/CricAI)
