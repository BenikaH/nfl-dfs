#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime

def getweek():
    
    today = datetime.date.today()
    week1 = datetime.date(2015, 9, 8)       #### Tuesday of Week 1
    datedict = {}
    
    for i in range(1,18):
        datedict[i] = week1 + datetime.timedelta(days=7*(i-1))      #### Week Starting Tuesday
    
    for key in datedict.keys():
        if today >= datedict[key] and today < datedict[key + 1]:
            weekNum = key
            
    return weekNum

weekNum = getweek()

# firstPull = raw_input("Are these opening odds (y/n)? ")

headerList = ['Week', 'Date', 'Time', 'HomeAway', 'Team', 'Opp', 'Team Spread', 'Opp Spread', 'Total Points', 'Team Proj Score', 'Opp Proj Score', 'Opening Team Score', 'Opening Opp Score', 'Team Score Chg', 'Opp Score Chg']

local = False
if local == False:
    con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
else:
    con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection

with con:

# bring in past results
    cur = con.cursor()
    cur.execute("SELECT * FROM rotogrinders_odds WHERE week = %d" % (weekNum))

    rows = cur.fetchall()
    if len(rows) > 0:
        firstPull = 'n'
    else:
        firstPull = 'y'

# firstPull = 'y'         ### TEMPORARY TO SOLVE ISSUE

if firstPull.lower() != 'y':

    pastresults = []
    holder = []

    with con:

    # bring in past results
        cur = con.cursor()
        cur.execute("SELECT * FROM rotogrinders_odds WHERE week = %d" % (weekNum))

        rows = cur.fetchall()
        if len(rows) > 0:
            for row in rows:
                for item in row:
                    holder.append(item)
                pastresults.append(holder)
                holder = []

    # print pastresults

r = requests.get("https://rotogrinders.com/pages/nfl-vegas-odds-page-56651").text
soup = BeautifulSoup(r)

table = soup.find_all("tbody")[0]

gameSet = table.find_all("tr")

game = []
gameList = []

for rows in gameSet:
    items = rows.find_all("td")
    game.append(weekNum)
    for item in items:
        game.append(item.text.strip().replace('    ',' '))
    for i in range(0,3):
        game.append(0.00)
    gameList.append(game)
    game = []

# print gameList

####### Convert results into individual lines by team
hmorder = [0,1,2,4,3,6,5,7,9,8]
aworder = [0,1,2,3,4,5,6,7,8,9]

holder = []
gameinfo = []

for game in gameList:
    # print game
    holder = [game[i] for i in hmorder]  # List method to put items into home team order
    holder.insert(3, 'Home')             # Add 'Home' to home teams
    gameinfo.append(holder)
    holder = [game[i] for i in aworder]  # List method to put items into away team order
    holder.insert(3, 'Away')             # Add 'Away' to away teams
    gameinfo.append(holder)

# print gameinfo[0]

if firstPull.lower() == 'y':
    for game in gameinfo:
        for i in range(0,4):
            game.append(0.00)
        game[11] = game[9]
        game[12] = game[10]
        game[13] = 0.00
        game[14] = 0.00
else:
    for game in gameinfo:
        for i in range(0,4):
            game.append(0.00)
        for pull in pastresults:
            # print pull
            # print game
            if game[4] == pull[5]:
                game[11] = pull[12]
                game[12] = pull[13]
                game[13] = round(float(game[9]),2) - round(float(game[11]),2)
                game[14] = round(float(game[10]),2) - round(float(game[12]),2)
                continue


#### Add to dictionary
# dictList = []
# for games in gameList:  # Create a dictionary from each row, then add to a list for csv export
#     gamedict = {}
#     for header in headerList:
#         gamedict[header] = games[headerList.index(header)]
#     dictList.append(gamedict)

####### Add to database

query = "DELETE FROM rotogrinders_odds WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in gameinfo:
    # print row
    with con:
        query = "INSERT INTO rotogrinders_odds (week, game_date, game_time, home_away, team, opp, team_spread, \
            opp_spread, total_pts, team_proj, opp_proj, team_proj_open, opp_proj_open, team_proj_chg, opp_proj_chg) \
            VALUES (%d, "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
            (int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], \
            row[8], row[9], row[10], row[11], row[12], row[13], row[14])
        x = con.cursor()
        x.execute(query)
