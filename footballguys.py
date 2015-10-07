#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import re
import time
import MySQLdb


####### Sign into Rotogrinders
# r = requests.get("http://subscribers.footballguys.com/amember/login.php")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
payload = {'amember_login':'MurrDogg4','amember_pass':'tro2bro', 'amember_redirect_url': 'http://www.footballguys.com'}

session = requests.Session()
session.post('https://rotogrinders.com/sign-in',headers=headers,data=payload)


####### Start Draftkings scrape
r = session.get("http://subscribers.footballguys.com/amember/login.php").text


def getfanduelproj(linkwk, site):    
    
    link = 'http://subscribers.footballguys.com/apps/article.php?article=tremblay_v15' + site + linkwk

    r = requests.get(link).text
    soup = BeautifulSoup(r)

    playerSet = soup.find_all('tr', {'class': ['QB', 'RB', 'WR', 'TE', 'D']})

    playerDict = {}
    playerList = []
    temp = []
    for player in playerSet:
        pl = player.find_all('td')
        playerDict['name'] = pl[0].text
        playerDict['pos'] = pl[3].text
        playerDict['game'] = pl[4].text
        playerDict['fd_salary'] = pl[5].text
        playerDict['mt_fdp'] = pl[6].text
        playerDict['dd_fdp'] = pl[7].text
        playerDict['sb_fdp'] = pl[8].text
        playerDict['av_fdp'] = pl[9].text
        playerDict['mtval_fdp'] = pl[10].text
        playerDict['ddval_fdp'] = pl[11].text
        playerDict['sbval_fdp'] = pl[12].text
        playerDict['avval_fdp'] = pl[13].text
        playerDict['mthval_fdp'] = pl[14].text
        playerDict['ddhval_fdp'] = pl[15].text
        playerDict['sbhval_fdp'] = pl[16].text
        playerDict['avhval_fdp'] = pl[17].text
        playerList.append(playerDict)
        playerDict = {}

    return playerList


# f = open('nfl-dfs/weekinfo.txt', 'r')
f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])

if weekNum < 10:
    linkwk = '0' + str(weekNum)
else:
    linkwk = str(weekNum)
    
site = ['FanDuel', 'DraftKings']

print getfanduelproj(linkwk, site[0])