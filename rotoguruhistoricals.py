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


def getweeklyresults(weekNm):
    
    positions = ['Quarterbacks', 'Running Backs', 'Wide Receivers', 'Tight Ends', 'Defenses']
    posabbr = ['QB', 'RB', 'WR', 'TE', 'D']
    ### Start with DraftKings results for the week
    r = requests.get("http://rotoguru1.com/cgi-bin/fyday.pl?week=" + str(weekNm) + "&game=dk").text

    soup = BeautifulSoup(r)
    playerSet = soup.find_all("tr")
    boldind = []
    playerSet = [t for t in playerSet if (not t.find_all("hr"))]
    for i in playerSet:
        rows = i.find_all("td")
        for row in rows:
            if row.find("b"):
                if row.text.strip() in positions:
                    boldind.append(playerSet.index(i))
    
    # get list of positions and indexes
    boldind1 = boldind[0]
    boldind = [i-boldind.index(i) for i in boldind[1:]]     ### Do I need to make this -1 for local??
    boldind[-1] = boldind[-1] - 1               ## Adjusts for Kicker
    boldind.insert(0,boldind1)
    
    userows = [t for t in playerSet if (not t.find_all("hr") and not t.find_all("b"))]
    counter = 0
    playerList = []
    player = []
    for players in userows[6:]:
        if userows.index(players) in boldind[1:]:   ### To indicate the current position
            counter += 1
        player.append(weekNm)       # Add week number to each player line
        links = players.find("a")   # Add player ID
        plLink = links['href']
        plid = plLink[plLink.index('cgi?')+4:]
        player.append(plid)
        rows = players.find_all("td")
        for row in rows:
            player.append(row.text)
        playerNm = player[2].split(', ')        # Split name into last name and first name
        if len(playerNm) == 2:
            player.append(playerNm[0])
            player.append(playerNm[1])
        else:
            for i in range(0,2):
                player.append('')
        for i in range(0,2):
            player.append(0)
        player.append(posabbr[counter])     # Add position
        playerList.append(player)
        player = []

    ### Get FanDuel results
    r = requests.get("http://rotoguru1.com/cgi-bin/fyday.pl?week=" + str(weekNm) + "&game=fd").text

    soup = BeautifulSoup(r)

    playerSet = soup.find_all("tr")
    userows = [t for t in playerSet if (not t.find_all("hr") and not t.find_all("b"))]

    fdplayerList = []
    player = []
    for players in userows[6:]:
        if userows.index(players) in boldind:
            counter += 1
        player.append(weekNm)       # Add week number to each player line
        links = players.find("a")   # Add player ID
        plLink = links['href']
        plid = plLink[plLink.index('cgi?')+4:]
        player.append(plid)
        rows = players.find_all("td")
        for row in rows:
            player.append(row.text)
        fdplayerList.append(player)
        player = []

    for dkplayers in playerList:
        for fdplayers in fdplayerList:
            if dkplayers[1] == fdplayers[1]:
                dkplayers[9] = fdplayers[5]
                dkplayers[10] = fdplayers[6]
                continue
    return playerList


def main():
    
    runtoday = True
    # Only run on Tuesday
    weekday = datetime.date.today().isoweekday()
    if weekday == 2:
        runtoday = True
    else:
        print "Not Tuesday"
    
    if runtoday:    
        # f = open('weekinfo.txt', 'r')             ### Local
        # f = open('nfl-dfs/weekinfo.txt', 'r')
        # ftext = f.read().split(',')
        # weekNum = int(ftext[0])-1
        weekNum = getweek() - 1

        masterList = []

        weeklyresult = getweeklyresults(weekNum)
        # for i in range(1,18):
        #     weeklyresult = getweeklyresults(i)

        for row in weeklyresult:
            masterList.append(row)
        # print "Week %d Complete" % (i)

        for row in masterList:
            row[1] = int(row[1])
            row[5] = round(float(row[5]),2)
            row[9] = round(float(row[9]),2)
            try:
                row[6] = int(row[6].replace('$','').replace(',',''))
            except:
                row[6] = 0
            try:
                row[10] = int(row[10].replace('$','').replace(',',''))
            except:
                row[10] = 0

        listlen = len(masterList)
        print masterList
        #
        local = False
        if local == False:
            con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
        else:
            con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection

        query = "DELETE FROM dfs_results_2015 WHERE week = %d" % (weekNum)
        x = con.cursor()
        x.execute(query)

        for row in masterList:
            with con:
                query = "INSERT INTO dfs_results_2015 (week, player_id, playernm_full, team, opp, dkp, dk_salary, playernm_last, playernm_first, fdp, fd_salary, pos) \
                VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", %1.2f, %d, "'"%s"'", "'"%s"'", %1.2f, %d, "'"%s"'")" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
                x = con.cursor()
                x.execute(query)
            if masterList.index(row) % 100 == 0:
                print str(masterList.index(row)) + " out of " + str(listlen)


if __name__ == '__main__':
    main()