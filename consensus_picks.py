#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
import MySQLdb
import csv

r = requests.get("http://www.oddsshark.com/nfl/consensus-picks").text

soup = BeautifulSoup(r)

data = soup.find('table', {'class': 'base-table'})

games = data.find_all('tr')

gameset = []

for rows in games[1:]:
    temp = []
    for item in rows.find_all('td'):
        if '@' in item.text:
            consensus = item.find('span', {'class': 'highlighted'}).text.strip()
            temp.append(consensus)
            teams = item.text.strip().split('@')
            for team in teams:
                temp.append(team.strip())
        elif '%' in item.text:
            pct = int(item.text[:-1])/100.0
            temp.append(pct)
        else:
            temp.append(item.text.strip())
    gameset.append(temp)
    temp = []

betlist = []
for game in gameset:
    gamedict = {}
    if game[0] == game[1]:
        gamedict['team'] = game[1]
        gamedict['opp'] = game[2]
        gamedict['spread'] = float(game[3])
        gamedict['consensus'] = round(game[4], 2)
        betlist.append(gamedict)
        gamedict = {}
        gamedict['team'] = game[2]
        gamedict['opp'] = game[1]
        gamedict['spread'] = -float(game[3])
        gamedict['consensus'] = round(1.0 - game[4], 2)
        betlist.append(gamedict)
    else:
        gamedict['team'] = game[2]
        gamedict['opp'] = game[1]
        gamedict['spread'] = float(game[3])
        gamedict['consensus'] = round(game[4], 2)
        betlist.append(gamedict)
        gamedict = {}
        gamedict['team'] = game[1]
        gamedict['opp'] = game[2]
        gamedict['spread'] = -float(game[3])
        gamedict['consensus'] = round(1.0 - game[4], 2)
        betlist.append(gamedict)
        
print betlist

teamlist = []
# Bring in team list
# with open('nfl-dfs/team_list.csv') as f:
with open('team_list.csv', 'rU') as f:
    w = csv.DictReader(f)
    for row in w:
        teamlist.append(row)
    
print teamlist