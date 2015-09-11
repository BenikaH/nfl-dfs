#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import re
import time
import MySQLdb

f = open('nfl-dfs/weekinfo.txt', 'r')
# f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])

# weekNum = int(raw_input("Week number? "))

posSet = ["QB", "RB", "WR", "TE"]

playerList = []
def getPlayerProj(weekNum, position, playerList):
    link = "http://www.fantasypros.com/nfl/projections/" + position.lower() + ".php?week="+str(weekNum)
    time.sleep(2)
    r = requests.get(link).text
    soup = BeautifulSoup(r)
    playerSet = soup.find_all("tr", class_="mpb-available")

    player = []

    for players in playerSet:
        player.append(weekNum)
        player.append(position)
        row = players.find_all("td")
        plLink = row[0].find_all("a")
        plLink = plLink[1]["class"][1]
        testing = re.finditer('-.+-',plLink)        # Search player ID link for the ID using firstnm-lastnm-ID
        for i in testing:
            pidchar = i.span()[1]                   # Gets the span (start, end) of the regex and uses the end
        plID = int(plLink[pidchar:])                     # Get the ID from the link using pidchar as the start char
        player.append(plID)
        team = row[0].find_all("small")
        try:
            player.append(team[0].text)
        except:
            player.append('')
        for item in row:
            for tag in item.find_all('span', class_="label"):        # Remove span tags that have prob/quest/etc. in them
                tag.replace_with('')
            for tag in item.find_all('small'):
                tag.replace_with('')
            player.append(item.text.strip())
        if position == "QB":
            for i in range(0,3):
                player.insert(13,0.00)
        elif position == "TE":
            for i in range(0,8):
                player.insert(5,0.00)
        else:
            for i in range(0,5):
                player.insert(5,0.00)
        
        dkscore = fantasyscore(player)[0]
        fdscore = fantasyscore(player)[1]
        player.append(dkscore)
        player.append(fdscore)    
        playerList.append(player)
        player = []
    
    return playerList

def fantasyscore(player):
    
    passbonus = 0
    recbonus = 0
    rushbonus = 0
    
    if float(player[7]) >= 300.0:
        passbonus = 1
    if float(player[11]) >= 100.0:
        rushbonus = 1
    if float(player[14]) >= 100.0:
        recbonus = 1
        
    dkscore = (float(player[8]) * 4) + (float(player[7]) * 0.04) - (float(player[9]) * 1) + (float(player[12]) * 6) + \
    (float(player[11]) * 0.1) + (float(player[15]) * 6) + (float(player[14]) * 0.1) + (float(player[13]) * 1) - \
    (float(player[16]) * 1) + (passbonus * 3) + (recbonus * 3) + (rushbonus * 3)
    
    fdscore = (float(player[8]) * 4) + (float(player[7]) * 0.04) - (float(player[9]) * 1) + (float(player[12]) * 6) + \
    (float(player[11]) * 0.1) + (float(player[15]) * 6) + (float(player[14]) * 0.1) + (float(player[13]) * 0.5) - \
    (float(player[16]) * 2)
    
    fpts = [round(dkscore,2), round(fdscore,2)]
    
    return fpts



for pos in posSet:
    getPlayerProj(weekNum, pos, playerList)
    print pos, "complete"

print playerList

####### Add to database

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')

query = "DELETE FROM fantasypros_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        query = "INSERT INTO fantasypros_wkly_proj (week, pos, player_id, team, playernm_full, \
        pass_att, pass_cmp, pass_yds, pass_td, ints, rush_att, rush_yds, rush_td, rec, rec_yds, \
        rec_td, fumbles_lost, fpts, dkp, fdp) \
        VALUES (%d, "'"%s"'", %d, "'"%s"'", "'"%s"'", %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, \
        %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f)" % \
        (int(row[0]), row[1], int(row[2]), row[3], row[4], \
        round(float(row[5]),2), round(float(row[6]),2), round(float(row[7]),2), round(float(row[8]),2), \
        round(float(row[9]),2), round(float(row[10]),2), round(float(row[11]),2), \
        round(float(row[12]),2), round(float(row[13]),2), round(float(row[14]),2), round(float(row[15]),2), \
        round(float(row[16]),2), round(float(row[17]),2), round(float(row[18]),2), round(float(row[19]),2))
        x = con.cursor()
        x.execute(query)

