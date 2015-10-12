#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import re
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


def getFoxProj(page, weekNum):
    
    r = requests.get("http://www.foxsports.com/fantasy/football/commissioner/Research/Projections.aspx?page=" + str(page) + "&position=-1&split=4&playerSearchStatus=1").text
    soup = BeautifulSoup(r)
    
    playerTable = soup.find("tbody")
    
    playerSet = playerTable.find_all("tr")
    player = []
    for rows in playerSet:
        try:
            teampos = rows.find_all("div", class_="TeamPosPlayerInfo")[0].text.replace('(','').replace(')','').replace(' ','')
            team = teampos.split('-')[0]
            pos = teampos.split('-')[1]
        except:
            teampos = ''
            team = ''
            pos = ''
        for tag in rows.find_all("td", class_="status"):
            tag.replace_with('')
        for tag in rows.find_all("span"):
            tag.replace_with('')    
        plLink = rows.find("a")
        plLink = plLink['href']
        plID = plLink[plLink.index("player")+7:]
        player.append(weekNum)
        player.append(int(plID))
        row = rows.find_all("td")
        for item in row:
            for tag in item.find_all("div", class_="TeamPosPlayerInfo"):
                tag.replace_with('')
            player.append(item.text.strip())
        player.insert(3,pos)
        player.insert(3,team)
        playerList.append(player)
        player = []
    
    print page, "complete"  
    return playerList
    
def fantasyscore(player):
    
    passbonus = 0
    recbonus = 0
    rushbonus = 0
    
    if float(player[6]) >= 300.0:
        passbonus = 1
    if float(player[11]) >= 100.0:
        rushbonus = 1
    if float(player[14]) >= 100.0:
        recbonus = 1
        
    dkscore = (float(player[5]) * 4) + (float(player[6]) * 0.04) - (float(player[9]) * 1) + (float(player[10]) * 6) + \
    (float(player[11]) * 0.1) + (float(player[13]) * 6) + (float(player[14]) * 0.1) + (float(player[15]) * 1) + \
    (float(player[16]) * 2) - (float(player[18]) * 1) + (passbonus * 3) + (recbonus * 3) + (rushbonus * 3)
    
    fdscore = (float(player[5]) * 4) + (float(player[6]) * 0.04) - (float(player[9]) * 1) + (float(player[10]) * 6) + \
    (float(player[11]) * 0.1) + (float(player[13]) * 6) + (float(player[14]) * 0.1) + (float(player[15]) * 0.5) + \
    (float(player[16]) * 2) - (float(player[18]) * 2)
    
    fpts = [round(dkscore,2), round(fdscore,2)]
    
    return fpts
    
# f = open('weekinfo.txt', 'r')             ### Local
# f = open('nfl-dfs/weekinfo.txt', 'r')
# ftext = f.read().split(',')
# weekNum = int(ftext[0])
weekNum = getweek()

# weekNum = int(raw_input("Week number? "))
   
r = requests.get("http://www.foxsports.com/fantasy/football/commissioner/Research/Projections.aspx?page=1&position=-1&split=4&playerSearchStatus=1").text
soup = BeautifulSoup(r)

page = soup.find("a", {"id" : "MainColumn_LastPageLink"})
print page
lastpage = int(page.text)
print lastpage
playerList = []
for i in range(1,lastpage):
    getFoxProj(i,weekNum)
    
for player in playerList:
    for item in player:
        if item == '--':
            player[player.index(item)] = '0.00'
            # item = item.replace('--','0.00')
    dkscore = fantasyscore(player)[0]
    fdscore = fantasyscore(player)[1]
    player.append(dkscore)
    player.append(fdscore)
print playerList[:2]




####### Add to database

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')


query = "DELETE FROM foxsports_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        query = "INSERT INTO foxsports_wkly_proj (week, player_id, playernm_full, team, pos, \
        pass_td, pass_yds, pass_att, pass_cmp, ints, rush_td, rush_yds, rush_att, rec_td, rec_yds, \
        rec, twopt_conv, fumble_recovery_td, fumbles_lost, fpts, dkp, fdp) \
        VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, \
        %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f)" % \
        (int(row[0]), int(row[1]), row[2], row[3], row[4], \
        round(float(row[5]),2), round(float(row[6]),2), round(float(row[7]),2), round(float(row[8]),2), \
        round(float(row[9]),2), round(float(row[10]),2), round(float(row[11]),2), \
        round(float(row[12]),2), round(float(row[13]),2), round(float(row[14]),2), round(float(row[15]),2), \
        round(float(row[16]),2), round(float(row[17]),2), round(float(row[18]),2), round(float(row[19]),2), \
        round(float(row[20]),2), round(float(row[21]),2))
        x = con.cursor()
        x.execute(query)

