#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
import MySQLdb

# 0 Week, Player ID, Player Name, Opp, Status, 5 Pass C/A, Pass Yds, Pass TD, Ints, Rush, 10 Rush Yds, Rush TD, Rec, Rec Yds, Rec TD

def espnscrape(weekNum):
    
    startInd = 0
    playerList = []
    playerscore = 0         ### Indicator for if we should keep running
    
    while playerscore == 0:
        print startInd
        r = requests.get("http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId="+ str(weekNum) +"&seasonId=2015&startIndex=0"+str(startInd)).text
        soup = BeautifulSoup(r)
        table = soup.find("table")
        playerSet = table.find_all("tr", {"class" : "pncPlayerRow"})
        player = []

        for players in playerSet:
            player.append(weekNum)
            links = players.find("a")   # Add player ID
            plID = links['playerid']
            player.append(plID)
            rows = players.find_all("td")
            for row in rows:
                player.append(row.text.strip())
            if player[-1] == '0':
                playerscore = 1
            dkscore = round(fantasyscore(player)[0],2)
            fdscore = round(fantasyscore(player)[1],2)
            
            if "D/ST" not in player[2]:
                playerinfo = player[2].split(',')
                name = playerinfo[0]
                team = playerinfo[1].strip().split()[0]
                pos = playerinfo[1].strip().split()[1]
        
                output = []
                output.append(weekNum)
                output.append(int(plID))
                output.append(pos)
                output.append(name)
                output.append(team)
                output.append(dkscore)
                output.append(fdscore)
                print output
                playerList.append(output)
            player = []
            output = []
        
        startInd += 40
        
    return playerList
    

def fantasyscore(player):
    
    passbonus = 0
    recbonus = 0
    rushbonus = 0
    
    if float(player[6]) >= 300.0:
        passbonus = 1
    if float(player[10]) >= 100.0:
        rushbonus = 1
    if float(player[13]) >= 100.0:
        recbonus = 1
    
    dkscore = (float(player[6]) * 0.04) + (float(player[7]) * 4) - (float(player[8])) + (float(player[10]) * 0.10) + \
    (float(player[11]) * 6) + (float(player[12]) * 1) + (float(player[13]) * 0.10) + (float(player[14]) * 6) + (passbonus * 3) + (rushbonus * 3) + (recbonus * 3)
    
    fdscore = (float(player[6]) * 0.04) + (float(player[7]) * 4) - (float(player[8])) + (float(player[10]) * 0.10) + \
    (float(player[11]) * 6) + (float(player[12]) * 0.5) + (float(player[13]) * 0.10) + (float(player[14]) * 6)
    
    fpts = [dkscore, fdscore]
    return fpts

# f = open('weekinfo.txt', 'r')             ### Local
f = open('nfl-dfs/weekinfo.txt', 'r')
ftext = f.read().split(',')
weekNum = int(ftext[0])
    
playerList = espnscrape(weekNum)

####### Add to database

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')


query = "DELETE FROM espn_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        query = "INSERT INTO espn_wkly_proj (week, player_id, pos, playernm_full, team, dkp, fdp) \
        VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", %1.2f, %1.2f)" % \
        (int(row[0]), int(row[1]), row[2], row[3], row[4], round(float(row[5]),2), round(float(row[6]),2))
        x = con.cursor()
        x.execute(query)