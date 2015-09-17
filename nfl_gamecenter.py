#!/usr/local/bin/python2.7
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


import requests
import re
import time

Years = ['2013','2014','2015']
Weeks = [x for x in xrange(1,18)]

### Need the function to bring in all information about each indivdual game and store it
def getgameids(week, year):
    r = requests.get("http://www.nfl.com/ajax/scorestrip?season="+str(year)+"&seasonType=REG&week="+str(week)).text

    root = ET.fromstring(r)

    gms = root[0]
    xmlist = ['eid', 'd', 't', 'q', 'h', 'hnn', 'hs', 'v', 'vnn', 'vs']
    gametemp = {}
    gameids = []
    try:
        for g in gms:
            for l in xmlist:
                gametemp[l] = g.get(l)
            gameids.append(gametemp)
    except:
        print "error"
    
    return gameids

def gamelist(weeks, years):
    gameList = []
    for season in years:
        for weekNum in weeks:
            games = getgameids(weekNum, season)
            for game in games:
                gameList.append(game)
            print "Week %s Complete - Year %s" % (str(weekNum), season)
        time.sleep(1)
    return gameList


#### 
# Player Profile IDs are set up like the following:
#   GSIS IDs (gamecenter ID) can be used to create profiles like: http://www.nfl.com/players/profile?id=00-0030110
#   This would then load the default url of http://www.nfl.com/player/michaelwilliams/2539197/profile

# We should go through all of the data, pulling the relevant information for passing, receiving, etc.
# Gather it into a dictionary based on GSIS
# Later go through all the GSIS IDs to get all the information on each player



def getplayerid(player_gsis):       ### Returns the player ID based on gsis ID from Game Center
    r = requests.get("http://www.nfl.com/players/profile?id="+str(player_gsis))
    urlnm = r.url
    m = re.search('/([0-9]+)/', urlnm)
    return None if m is None else int(m.group(1))

def searchforid(player_gsis):
    return player_gsis

def getgamedata(game_id, dateinfo, playerIDdict, gamelist):
    
    passkeys = ['att', 'cmp', 'yds', 'tds', 'ints', 'twopta', 'twoptm']
    passkeynm = ['pass_att', 'pass_cmp', 'pass_yds', 'pass_td', 'ints', 'pass_twopta', 'pass_twoptm']
    rushkeys = ['att', 'yds', 'tds', 'lng', 'lngtd', 'twopta', 'twoptm']
    rushkeynm = ['rush_att', 'rush_yds', 'rush_tds', 'rush_lng', 'rush_lngtd', 'rush_twopta', 'rush_twoptm']
    reckeys = ['rec', 'yds', 'tds', 'lng', 'lngtd', 'twopta', 'twoptm']
    reckeynm = ['rec', 'rec_yds', 'rec_tds', 'rec_lng', 'rec_lngtd', 'rec_twopta', 'rec_twoptm']
    hmaway = ['home', 'away']
    
    r = requests.get("http://www.nfl.com/liveupdate/game-center/"+game_id['eid']+"/"+game_id['eid']+"_gtd.json")
    data = r.json()
    gameinfo = data[game_id['eid']]
    
    gamedict, homekeys, awaykeys = {}, {}, {}
    
    for team in hmaway:
        gamedict = {}
        rushinginfo = gameinfo[team]["stats"]["rushing"]
        recinfo = gameinfo[team]["stats"]["receiving"]
        passinfo = gameinfo[team]["stats"]["passing"]
        teamabbr = gameinfo[team]["abbr"]
        
        for key in rushinginfo.keys():          ### Get all the Keys and Names of players
            gamedict[key] = {"name": rushinginfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}
        for key in recinfo.keys():
            gamedict[key] = {"name": recinfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}
        for key in passinfo.keys():
            gamedict[key] = {"name": passinfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}


        for key in gamedict.keys():         #### Get rushing data for each player
            for keynm in rushkeys:
                if key in rushinginfo:
                    gamedict[key][rushkeynm[rushkeys.index(keynm)]] = rushinginfo[key][keynm]
                else:
                    gamedict[key][rushkeynm[rushkeys.index(keynm)]] = 0
            for keynm in reckeys:
                if key in recinfo:
                    gamedict[key][reckeynm[reckeys.index(keynm)]] = recinfo[key][keynm]
                else:
                    gamedict[key][reckeynm[reckeys.index(keynm)]] = 0
            for keynm in passkeys:
                if key in passinfo:
                    gamedict[key][passkeynm[passkeys.index(keynm)]] = passinfo[key][keynm]
                else:
                    gamedict[key][passkeynm[passkeys.index(keynm)]] = 0
            # Add game info to all the players        
            gamedict[key]['day'] = game_id['d']
            gamedict[key]['time'] = game_id['t']
            gamedict[key]['hmteam'] = game_id['h']
            gamedict[key]['hmscore'] = game_id['hs']
            gamedict[key]['awteam'] = game_id['v']
            gamedict[key]['awscore'] = game_id['vs']
            gamedict[key]['week'] = dateinfo[0]
            gamedict[key]['year'] = dateinfo[1]
        
        if team == 'home':
            homedict = gamedict
        else:
            awaydict = gamedict
    
    for keys in awaydict.keys():
        homedict[keys] = awaydict[keys]
        
    gamedict = homedict
    for key in gamedict:
        #### Need IF statement that only runs this if player ID hasn't been found yet.
        #### Just put all GSIS IDs and Player IDs in a separate dict and reference that.
        #### if idkey in idDict then gamedict[key]["player_id"] = searchforkey(key) else = getplayerid(key)
        if key not in playerIDdict.keys():
            gamedict[key]["player_id"] = getplayerid(key)
            playerIDdict[key] = getplayerid(key)
        else:
            gamedict[key]["player_id"] = playerIDdict[key]
    gamelist.append(gamedict)
    return gamelist

playerIDdict = {}
gamelist = []
year = 2014
for week in Weeks[:2]:
    for i in range(0,2):
        # week = 1
        # year = 2015
        dateinfo = [week, year]
        gameid = getgameids(dateinfo[0], dateinfo[1])[i]
        getgamedata(gameid, dateinfo, playerIDdict, gamelist)
    print year, ": week ", week, " complete"
    time.sleep(2)

print gamelist
                    
