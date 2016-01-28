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

def security(site,fldr):
    
    info = []
    myfile = fldr + 'myinfo.txt'

    siteDict = {}
    with open(myfile) as f:
        g = f.read().splitlines()
        for row in g:
            newlist = row.split(' ')
            siteDict[newlist[0]] = {}
            siteDict[newlist[0]]['username'] = newlist[1]
            siteDict[newlist[0]]['password'] = newlist[2]
                
    info = [siteDict[site]['username'],siteDict[site]['password']]
    
    return info

def main():
    headerList = ['playerID', 'pos', 'FullName', 'Lastname', 'Firstname', 'Team', 'Opp', 'Spread', 'OverUnder', 'ML', 'DKSalary', \
                'DKP', 'DKValue', 'FDSalary', 'FDP', 'FDValue', 'webLink']

    # f = open('weekinfo.txt', 'r')             ### Local
    # f = open('nfl-dfs/weekinfo.txt', 'r')
    # ftext = f.read().split(',')
    # weekNum = int(ftext[0])
    weekNum = getweek()

            
    r = requests.get("http://www.rotowire.com/daily/nfl/optimizer.htm?site=DraftKings").text
    soup = BeautifulSoup(r)

    playerSet = soup.find_all("tr", {"class" : "playerSet"})

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
        for row in rows[1:11]:
            for tag in row.find_all('span'):        # Remove span tags that have prob/quest/etc. in them
                tag.replace_with('')
            item = row.text.strip()
            if '$' in item:
                for char in item:
                    if char in "$ ,":
                        item = item.replace(char, '')
                item = int(item)
            player.append(item)
        for i in range(0,3):        # Placeholder for FD results
            player.append(0)
        player.append(plLink)
        playerList.append(player)
        player = []

    # print playerList

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
        for row in rows[1:11]:
            for tag in row.find_all('span'):        # Remove span tags that have prob/quest/etc. in them
                tag.replace_with('')
            item = row.text.strip()
            if '$' in item:
                for char in item:
                    if char in "$ ,":
                        item = item.replace(char, '')
                item = int(item)
            player.append(item)
        player.append(plLink)
        fdplayerList.append(player)
        player = []

    for dplayer in playerList:
        for fplayer in fdplayerList:
            if dplayer[0] == fplayer[0]:
                dplayer[11] = fplayer[8]
                dplayer[12] = float(fplayer[9])
                dplayer[13] = fplayer[10]
                continue

    ### Add first and last name
    for player in playerList:
        plname = player[2].split(', ')
        if len(plname) == 2:
            player.insert(3, plname[0])
            player.insert(3, plname[1])
        else:
            player.insert(3, '')
            player.insert(3, '')

    kicker = []
    for player in fdplayerList:
        if player[1] == 'K':
            plname = player[2].split(', ')
            if len(plname) == 2:
                player.insert(3, plname[1])
                player.insert(3, plname[0])
            else:
                player.insert(3, '')
                player.insert(3, '')
            player.insert(0, weekNum)
            kicker.append(player)
    print kicker

    local = False
    if local == False:
        fldr = 'nfl-dfs/'
        serverinfo = security('mysql', fldr)
        con = MySQLdb.connect(host='mysql.server', user=serverinfo[0], passwd=serverinfo[1], db='MurrDogg4$dfs-nfl')
    else:
        fldr = ''
        con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection

    query = "DELETE FROM rotowire_wkly_proj WHERE week = %d" % (weekNum)
    x = con.cursor()
    x.execute(query)

    for row in playerList:
        print row
        with con:
            query = "INSERT INTO rotowire_wkly_proj (week, player_id, pos, playernm_full, playernm_first, playernm_last, \
                team, opp, spread, over_under, ml, dk_salary, dkp, dk_value, fd_salary, fdp, fd_value, weblink) \
                    VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                    "'"%s"'", "'"%s"'", "'"%s"'", %d, %1.2f, %1.2f, %d, %1.2f, %1.2f, "'"%s"'")" % \
                    (weekNum, int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], \
                    row[7], row[8], row[9], int(row[10]), round(float(row[11]),2), round(float(row[12]),2), \
                    int(row[13]), round(float(row[14]),2), round(float(row[15]),2), row[16])
            x = con.cursor()
            x.execute(query)

    print "Player Table Complete"
    print "Starting Kicker Table..."

    ##### Kicker Table

    query = "DELETE FROM rwkickers_wkly_proj WHERE week = %d" % (weekNum)
    x = con.cursor()
    x.execute(query)

    for row in kicker:
        print row
        with con:
            query = "INSERT INTO rwkickers_wkly_proj (week, player_id, pos, playernm_full, playernm_last, \
                                                    playernm_first, team, opp, spread, over_under, \
                                                    ml, fd_salary, fdp, fd_value, weblink) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                    (row[0], row[1], row[2], row[3], row[4], \
                    row[5], row[6], row[7], row[8], row[9], \
                    row[10], row[11], row[12], row[13], row[14])
            x = con.cursor()
            x.execute(query)