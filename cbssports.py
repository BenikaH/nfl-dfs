#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
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

# QB
# 0 Week, Position, Player, Pass Att, Pass Cmp,  5 Pass Yds, Pass TDs, Ints, CmpPct, Rushing YAtt, 10 Rushing Att
# Rush Yds, Rush Avg, Rush TD, Fumbles Lost, 15 Fpts

# RB
# 0 Week, Position, Player, Rush Att, Rush Yd, 5 Rush Avg, Rush TD, Rec, Rec Yd, Rec Avg, 10 Rec TD, Fumbles Lost, FPts

# WR TE
# 0 Week, Position, Player, Rec, Rec Yd, 5 Rec Avg, Rec TD, Fumbles Lost, Fpts

def cbsdata(weekNum):
    
    posabbr = ['QB', 'RB', 'WR', 'TE']
    player = []
    playerList = []
    ### Start with DraftKings results for the week
    for pos in posabbr:
        r = requests.get("http://fantasynews.cbssports.com/fantasyfootball/stats/weeklyprojections/"+pos+"/"+str(weekNum)+"/avg/standard?&print_rows=9999").text
        soup = BeautifulSoup(r)
        playerSet = soup.find_all("tr", {"class" : ("row1", "row2")})
        
        for players in playerSet[1:]:
            links = players.find("a")   # Add player ID
            plLink = links['href'][36:]
            plID = plLink[:plLink.index('/')]
            rows = players.find_all("td")
            player.append(weekNum)
            player.append(pos)
            for row in rows:
                player.append(row.text)
            if player[1] == "QB":
                dkscore = round(qbscore(player)[0],2)
                fdscore = round(qbscore(player)[1],2)
            elif player[1] == "RB":
                dkscore = round(rbscore(player)[0],2)
                fdscore = round(rbscore(player)[1],2)
            else:
                dkscore = round(wrscore(player)[0],2)
                fdscore = round(wrscore(player)[1],2)
            
            playerinfo = player[2].split(',')
            name = playerinfo[0]
            team = playerinfo[1].strip()
            player[2] = name
            player.append(team)
            
            output = []
            output.append(player[0])
            output.append(int(plID))
            output.append(player[1])
            output.append(player[2])
            output.append(player[-1])
            output.append(dkscore)
            output.append(fdscore)
            
            playerList.append(output)
            output = []
            player = []
    return playerList

def qbscore(player):
    bonus = 0
    if float(player[5]) >= 300.0:
        bonus = 1
    fpts = []
    dkscore = (float(player[5]) * 0.04) + (float(player[6]) * 4) - (float(player[7])) + (float(player[11]) * 0.1) + (float(player[13]) * 6) - (float(player[14])) + (bonus * 3)
    fdscore = (float(player[5]) * 0.04) + (float(player[6]) * 4) - (float(player[7])) + (float(player[11]) * 0.1) + (float(player[13]) * 6) - (float(player[14]) * 2)
    fpts.append(dkscore)
    fpts.append(fdscore)
    return fpts
    
def rbscore(player):
    rushbonus = 0
    recbonus = 0
    if float(player[4]) >= 100.0:
        rushbonus = 1
    if float(player[8]) >= 100.0:
        recbonus = 1
    fpts = []
    dkscore = (float(player[4]) * 0.1) + (float(player[6]) * 6) + (float(player[7]) * 1) + (float(player[8]) * 0.1) + \
    (float(player[10]) * 6)  - (float(player[11])) + (rushbonus * 3) + (recbonus * 3)
    fdscore = (float(player[4]) * 0.1) + (float(player[6]) * 6) + (float(player[7]) * 0.5) + (float(player[8]) * 0.1) + \
    (float(player[10]) * 6)  - (float(player[11]) * 2)
    fpts.append(dkscore)
    fpts.append(fdscore)
    return fpts

def wrscore(player):
    recbonus = 0
    if float(player[4]) >= 100.0:
        recbonus = 1
    fpts = []
    dkscore = (float(player[3]) * 1) + (float(player[4]) * 0.1) + (float(player[6]) * 6) - (float(player[7])) + (recbonus * 3)
    fdscore = (float(player[3]) * 0.5) + (float(player[4]) * 0.1) + (float(player[6]) * 6) - (float(player[7]) * 2)
    fpts.append(dkscore)
    fpts.append(fdscore)
    return fpts


local = False
if local == False:
    fldr = 'nfl-dfs/'
    con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
else:
    fldr = ''
    con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection
    
# f = open('weekinfo.txt', 'r')             ### Local
# f = open('nfl-dfs/weekinfo.txt', 'r')
# ftext = f.read().split(',')
# weekNum = int(ftext[0])
weekNum = getweek()
    
playerList = cbsdata(weekNum)

query = "DELETE FROM cbssports_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        query = "INSERT INTO cbssports_wkly_proj (week, player_id, pos, playernm_full, team, dkp, fdp) \
        VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", %1.2f, %1.2f)" % \
        (int(row[0]), int(row[1]), row[2], row[3], row[4], round(float(row[5]),2), round(float(row[6]),2))
        x = con.cursor()
        x.execute(query)

