from bs4 import BeautifulSoup
import requests
import csv
from datetime import date, datetime, timedelta
import time
import MySQLdb

tdate = date.today()
tdate = tdate.strftime("%m/%d/%Y")
r = requests.get("http://www.rotowire.com/daily/nfl/optimizer.htm?site=DraftKings").text
soup = BeautifulSoup(r)

weekNum = int(raw_input("Week number? "))
playerSet = soup.find_all("tr", {"class" : "playerSet"})

headerList = ['playerID', 'FullName', 'Team', 'Opp', 'Pos', 'DKSalary', 'DKP', 'DKValue', 'FirstName', 'LastName',\
 'FDSalary', 'FDP', 'FDValue', 'webLink']
player = []
playerList = []

for players in playerSet:
    links = players.find("a")
    plLink = links['href']
    try:
        plid = plLink[plLink.index('id=')+3:]
    except:
        plid = 99999
    player.append(plid)
    rows = players.find_all("td")
    for row in rows[1:-1]:
        for tag in row.find_all('span'):        # Remove span tags that have prob/quest/etc. in them
            tag.replace_with('')
        item = row.text.strip()
        if '$' in item:
            for char in item:
                if char in "$ ,":
                    item = item.replace(char, '')
            item = int(item)
        player.append(item)
    plname = player[1].split(', ')
    if len(plname) > 1:
        for i in plname:
            player.append(i)
    else:
        for i in range(0,2):
            player.append('')
    for i in range(0,3):        # Placeholder for FD results
        player.append(0)
    player.append(plLink)
    playerList.append(player)
    player = []

print playerList
# Fanduel Projections
r = requests.get("http://www.rotowire.com/daily/nfl/optimizer.htm?site=FanDuel").text
soup = BeautifulSoup(r)


playerSet = soup.find_all("tr", {"class" : "playerSet"})

player = []
fdplayerList = []

for players in playerSet:
    links = players.find("a")
    plLink = links['href']
    try:
        plid = plLink[plLink.index('id=')+3:]
    except:
        plid = 99999
    player.append(plid)
    rows = players.find_all("td")
    for row in rows[1:-1]:
        for tag in row.find_all('span'):        # Remove span tags that have prob/quest/etc. in them
            tag.replace_with('')
        item = row.text.strip()
        if '$' in item:
            for char in item:
                if char in "$ ,":
                    item = item.replace(char, '')
            item = int(item)
        player.append(item)
    plname = player[1].split(', ')
    if len(plname) > 1:
        for i in plname:
            player.append(i)
    else:
        for i in range(0,2):
            player.append('')
    player.append(plLink)
    fdplayerList.append(player)
    player = []

for dplayer in playerList:
    for fplayer in fdplayerList:
        if dplayer[0] == fplayer[0]:
            dplayer[10] = fplayer[5]
            dplayer[11] = float(fplayer[6])
            dplayer[12] = fplayer[7]
            continue
            

print playerList[:1]

con = MySQLdb.connect('localhost', 'root', '', 'test')

query = "DELETE FROM rotowire_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        query = "INSERT INTO rotowire_wkly_proj (week, player_id, playernm_full, team, opp, pos, dk_salary, \
            dkp, dk_value, playernm_first, playernm_last, fd_salary, fdp, fd_value, weblink) \
                VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", %d, %1.2f, %1.2f, "'"%s"'", "'"%s"'", \
                %d, %1.2f, %1.2f, "'"%s"'")" % \
                (weekNum, int(row[0]), row[1], row[2], row[3], row[4], row[5], \
            round(float(row[6]),2), round(float(row[7]),2), row[8], row[9], row[10], round(float(row[11]),2), round(float(row[12]),2), row[13])
        x = con.cursor()
        x.execute(query)