#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import re
import time
import MySQLdb
import time

# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

def getsiteproj(weekNum, site, playerDict):    
    
    # playerList = []
    if weekNum < 10:
        linkwk = '0' + str(weekNum)
    else:
        linkwk = str(weekNum)
    
    if site == 'FanDuel':
        abbr = 'fd'
        ptabbr = 'fdp'
    else:
        abbr = 'dk'
        ptabbr = 'dkp'
        
    payload = {'amember_login':'MurrDogg4','amember_pass':'tro2bro', 'amember_redirect_url': 'http://subscribers.footballguys.com/apps/article.php?article=tremblay_v15' + site + linkwk}

    session = requests.Session()
    session.post('http://subscribers.footballguys.com/amember/login.php', data=payload)
    
    link = 'http://subscribers.footballguys.com/apps/article.php?article=tremblay_v15' + site + linkwk
    r = session.get(link)
    if r.status_code == requests.codes.ok:
        r = r.text
        soup = BeautifulSoup(r)
        players = soup.find('table', id='players')
        playerSet = players.find_all('tr', {'class': ['QB', 'RB', 'WR', 'TE', 'D']})

        temp = []
        for player in playerSet:
            pl = player.find_all('td')
            name = pl[0].text
            if name not in playerDict.keys():
                playerDict[name] = {}
            playerDict[name]['pos'] = pl[3].text
            playerDict[name]['game'] = pl[4].text
            playerDict[name][abbr+'_salary'] = pl[5].text
            playerDict[name]['mt_'+ptabbr] = pl[6].text
            playerDict[name]['dd_'+ptabbr] = pl[7].text
            playerDict[name]['sb_'+ptabbr] = pl[8].text
            playerDict[name]['av_'+ptabbr] = pl[9].text
            playerDict[name]['mtval_'+ptabbr] = pl[10].text
            playerDict[name]['ddval_'+ptabbr] = pl[11].text
            playerDict[name]['sbval_'+ptabbr] = pl[12].text
            playerDict[name]['avval_'+ptabbr] = pl[13].text
            playerDict[name]['mthval_'+ptabbr] = pl[14].text
            playerDict[name]['ddhval_'+ptabbr] = pl[15].text
            playerDict[name]['sbhval_'+ptabbr] = pl[16].text
            playerDict[name]['avhval_'+ptabbr] = pl[17].text
            playerDict[name]['week'] = weekNum
            # playerList.append(playerDict)
            # playerDict = {}

    return playerDict

def addtoDb(con, weekNum, playerDict):
    
    query = "DELETE FROM footballguys_wkly_proj WHERE week = %d" % (weekNum)
    x = con.cursor()
    x.execute(query)

    for key in playerDict.keys():
        with con:
            query = "INSERT INTO footballguys_wkly_proj (playernm_full, week, pos, game, fd_salary, dk_salary, mt_fdp, dd_fdp, \
                    sb_fdp, av_fdp, mtval_fdp, ddval_fdp, sbval_fdp, avval_fdp, mthval_fdp, ddhval_fdp, \
                    sbhval_fdp, avhval_fdp, mt_dkp, dd_dkp, sb_dkp, av_dkp, mtval_dkp, ddval_dkp, \
                    sbval_dkp, avval_dkp, mthval_dkp, ddhval_dkp, sbhval_dkp, avhval_dkp) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (key, playerDict[key]['week'], playerDict[key]['pos'], playerDict[key]['game'], playerDict[key]['fd_salary'], playerDict[key]['dk_salary'], playerDict[key]['mt_fdp'], playerDict[key]['dd_fdp'], \
                playerDict[key]['sb_fdp'], playerDict[key]['av_fdp'], playerDict[key]['mtval_fdp'], playerDict[key]['ddval_fdp'], playerDict[key]['sbval_fdp'], playerDict[key]['avval_fdp'], playerDict[key]['mthval_fdp'], playerDict[key]['ddhval_fdp'], \
                playerDict[key]['sbhval_fdp'], playerDict[key]['avhval_fdp'], playerDict[key]['mt_dkp'], playerDict[key]['dd_dkp'], playerDict[key]['sb_dkp'], playerDict[key]['av_dkp'], playerDict[key]['mtval_dkp'], playerDict[key]['ddval_dkp'], \
                playerDict[key]['sbval_dkp'], playerDict[key]['avval_dkp'], playerDict[key]['mthval_dkp'], playerDict[key]['ddhval_dkp'], playerDict[key]['sbhval_dkp'], playerDict[key]['avhval_dkp'])
            x = con.cursor()
            x.execute(query)
            
    return

def cleandict(playerDict):
    dictkeys = ['week', 'pos', 'game', 'fd_salary', 'dk_salary', 'mt_fdp', 'dd_fdp', \
                'sb_fdp', 'av_fdp', 'mtval_fdp', 'ddval_fdp', 'sbval_fdp', 'avval_fdp', 'mthval_fdp', 'ddhval_fdp', \
                'sbhval_fdp', 'avhval_fdp', 'mt_dkp', 'dd_dkp', 'sb_dkp', 'av_dkp', 'mtval_dkp', 'ddval_dkp', \
                'sbval_dkp', 'avval_dkp', 'mthval_dkp', 'ddhval_dkp', 'sbhval_dkp', 'avhval_dkp']
                    
    for player in playerDict.keys():
        for key in dictkeys:
            if key not in playerDict[player].keys():
                playerDict[player][key] = 0.0
                
    return playerDict

def main():
    
    local = False
    if local == False:
        fldr = 'nfl-dfs/'
    else:
        fldr = ''

    if local == True:
        con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
    else:
        con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
        
    ##### Get week number
    f = open(fldr + 'weekinfo.txt', 'r')
    ftext = f.read().split(',')
    weekNum = int(ftext[0])
    
    sites = ['FanDuel', 'DraftKings']
    
    weeks = [2,3,4,5]
    for weekNum in weeks:
        playerDict = {}

        for site in sites:
            playerDict = getsiteproj(weekNum, site, playerDict)
            time.sleep(3)
    
        playerDict = cleandict(playerDict)

        addtoDb(con, weekNum, playerDict)
    
        print "Week ", weekNum, "database add complete"

if __name__ == '__main__':
    main()