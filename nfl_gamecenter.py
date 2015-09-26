#!/usr/local/bin/python2.7
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
import requests
import re
import time
import csv
import MySQLdb

Years = [2013,2014]
Weeks = [x for x in range(1,18)]
print Weeks
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
            gametemp = {}

    except:
        print "error"
    return gameids

# def gamelist(weeks, years):
#     gameList = []
#     for season in years:
#         for weekNum in weeks:
#             games = getgameids(weekNum, season)
#             for game in games:
#                 gameList.append(game)
#             print "Week %s Complete - Year %s" % (str(weekNum), season)
#         time.sleep(1)
#     return gameList


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
    soup = BeautifulSoup(r.text)
    
    playerinfo = soup.find("div", {"class" : "player-info"})
    spans = playerinfo.find_all("span")
    playernm = spans[0].text.strip()
    if len(spans) < 2:
        playerpos = None
    else:
        playerpos = spans[1].text.strip().split()[1]
    
    plinfo = [int(m.group(1)), urlnm, playernm, playerpos]

    return None if m is None else plinfo

def searchforid(player_gsis):
    return player_gsis

def getgamedata(game_id, dateinfo, playerIDdict, gamelist):
    
    passkeys = ['att', 'cmp', 'yds', 'tds', 'ints', 'twopta', 'twoptm']
    passkeynm = ['pass_att', 'pass_cmp', 'pass_yds', 'pass_tds', 'ints', 'pass_twopta', 'pass_twoptm']
    rushkeys = ['att', 'yds', 'tds', 'lng', 'lngtd', 'twopta', 'twoptm']
    rushkeynm = ['rush_att', 'rush_yds', 'rush_tds', 'rush_lng', 'rush_lngtd', 'rush_twopta', 'rush_twoptm']
    reckeys = ['rec', 'yds', 'tds', 'lng', 'lngtd', 'twopta', 'twoptm']
    reckeynm = ['rec', 'rec_yds', 'rec_tds', 'rec_lng', 'rec_lngtd', 'rec_twopta', 'rec_twoptm']
    hmaway = ['home', 'away']
    fumblekeys = ['tot', 'rcv', 'trcv', 'yds', 'lost']
    
    #### NEED TO BRING IN FUMBLES!!! "fumbles":{"00-0027983":{"name":"R.Moore","tot":1,"rcv":0,"trcv":0,"yds":0,"lost":0},"00-0030246":{"name":"J.Tuggle","tot":0,"rcv":1,"trcv":1,"yds":0,"lost":0}},"kicking":{"00-0029421":{"name":"R.Bullock","fgm":1,"fga":1,"fgyds":43,"totpfg":3,"xpmade":2,"xpmissed":0,"xpa":2,"xpb":0,"xptot":2}},"punting":{"00-0019714":{"name":"S.Lechler","pts":8,"yds":388,"avg":43,"i20":3,"lng":60}},"kickret":{"00-0031932":{"name":"C.Worthy","ret":1,"avg":27,"tds":0,"lng":27,"lngtd":0}},"puntret":{"00-0031600":{"name":"K.Mumphery","ret":6,"avg":9,"tds":0,"lng":15,"lngtd":0}}
    
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
        try:
            fumbles = gameinfo[team]["stats"]["fumbles"]
        except:
            fumbles = {}
        
        for key in rushinginfo.keys():          ### Get all the Keys and Names of players
            gamedict[key] = {"name": rushinginfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}
        for key in recinfo.keys():
            gamedict[key] = {"name": recinfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}
        for key in passinfo.keys():
            gamedict[key] = {"name": passinfo[key]["name"], "team": teamabbr, "game_id": game_id['eid']}
        for key in fumbles.keys():
            gamedict[key] = {"name": fumbles[key]["name"], "team": teamabbr, "game_id": game_id['eid']}


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
            if key in fumbles:
                gamedict[key]['fumbles_lost'] = fumbles[key]['lost']
            else:
                gamedict[key]['fumbles_lost'] = 0
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
        if key not in playerIDdict.keys():
            playerdtl = getplayerid(key)
            # gamedict[key]["player_id"] = playerdtl[0]
            playerIDdict[key] = {'player_id': playerdtl[0], 'url': playerdtl[1], 'name': playerdtl[2], \
                                'pos': playerdtl[3]}
        gamedict[key]["player_id"] = playerIDdict[key]
    gamelist.append(gamedict)
    return gamelist

def saveplayerdict(playerIDdict):
    dictlist = []
    headers = ['gsis_id', 'player_id', 'name', 'pos', 'url']
    # myfile = open('nfl-dfs/nflplayerids.csv', 'w+')
    # myfile.close()
    for key in playerIDdict.keys():
        newdict = {'gsis_id': key, 'player_id': playerIDdict[key]['player_id'], 'name': playerIDdict[key]['name'], \
        'pos': playerIDdict[key]['pos'], 'url': playerIDdict[key]['url']}
        dictlist.append(newdict)
        newdict = {}
    with open('nflplayerids.csv', 'wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(dictlist)
    print "playerlist saved to file"
    return

def openplayerdict():
    masterlist = []
    playerIDdict = {}
    with open('nflplayerids.csv') as f:
        w = csv.DictReader(f)
        for row in w:
            masterlist.append(row)
        for row in masterlist:
            playerIDdict[row['gsis_id']] = {'player_id': row['player_id'], 'name': row['name'], \
                                            'pos': row['pos'], 'url': row['url']}
    return playerIDdict
            
def tableinsert(gamelist):
    
    # {u'00-0025425': {'pass_twopta': 0, 'rec_tds': 0, 'pass_twoptm': 0, 'year': 2014, \
    # 'player_id': {'player_id': '2507170', 'url': 'http://www.nfl.com/player/zachmiller/2507170/profile', \
    # 'name': 'Zach Miller', 'pos': ''}, 'rec_twopta': 0, 'awscore': '16', 'ints': 0, 'game_id': '2014090400', \
    # 'rec_twoptm': 0, 'pass_att': 0, 'rush_yds': 0, 'pass_cmp': 0, 'rec_lngtd': 0, 'awteam': 'GB', \
    # 'hmteam': 'SEA', 'rush_att': 0, 'day': 'Thu', 'rush_lngtd': 0, 'pass_yds': 0, 'rec': 3, \
    # 'week': 1, 'time': '8:30', 'rush_tds': 0, 'rush_twopta': 0, 'rec_lng': 24, 'rush_twoptm': 0, \
    # 'rush_lng': 0, 'name': u'Z.Miller', 'pass_td': 0, 'hmscore': '36', 'team': u'SEA', 'rec_yds': 42}
    
    ### Open connection
    con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
    # con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
    
    # Remove data with same year -- no dupes
    query = "DELETE FROM nfl_gamecenter WHERE year = %d AND week = %d" % (year, week)
    x = con.cursor()
    x.execute(query)

    for player in gamelist:
        for key in player.keys():
            if player[key]['team'] == player[key]['hmteam']:
                home_away = "Home"
                opp = player[key]['awteam']
                score = player[key]['hmscore']
                opp_score = player[key]['awscore']
            else:
                home_away = "Away"
                opp = player[key]['hmteam']
                score = player[key]['awscore']
                opp_score = player[key]['hmscore']
            
            ##### DKP and FDP
            if player[key]['pass_yds'] >= 300:
                passbonus = 1
            else:
                passbonus = 0
            if player[key]['rush_yds'] >= 100:
                rushbonus = 1
            else:
                rushbonus = 0
            if player[key]['rec_yds'] >= 100:
                recbonus = 1
            else:
                recbonus = 0
            
            dkp = (player[key]['pass_yds'] * 0.04) + (player[key]['pass_tds'] * 4) - (player[key]['ints'] * 1) + \
                    (player[key]['rush_yds'] * 0.1) + (player[key]['rush_tds'] * 6) + (player[key]['rec'] * 1) + \
                    (player[key]['rec_yds'] * 0.1) + (player[key]['rec_tds'] * 6) + ((passbonus + rushbonus + recbonus) * 3) - \
                    (player[key]['fumbles_lost'] * 1)
            
            fdp = (player[key]['pass_yds'] * 0.04) + (player[key]['pass_tds'] * 4) - (player[key]['ints'] * 1) + \
                    (player[key]['rush_yds'] * 0.1) + (player[key]['rush_tds'] * 6) + (player[key]['rec'] * 0.5) + \
                    (player[key]['rec_yds'] * 0.1) + (player[key]['rec_tds'] * 6) - \
                    (player[key]['fumbles_lost'] * 2)
                                    
            with con:
                query = "INSERT INTO nfl_gamecenter (\
                year, \
                week, \
                start_time, \
                day, \
                game_id, \
                gsis_id, \
                player_id, \
                playernm_full, \
                playernm_gsis, \
                pos, \
                team, \
                home_away, \
                opp, \
                score, \
                opp_score, \
                pass_cmp, \
                pass_att, \
                pass_yds, \
                pass_tds, \
                ints, \
                pass_twopta, \
                pass_twoptm, \
                rush_att, \
                rush_yds, \
                rush_tds, \
                rush_lng, \
                rush_lngtd, \
                rush_twopta, \
                rush_twoptm, \
                rec, \
                rec_yds, \
                rec_tds, \
                rec_lng, \
                rec_lngtd, \
                rec_twopta, \
                rec_twoptm, \
                fumbles_lost, \
                dkp, \
                fdp, \
                url) \
                VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" \
                        % (player[key]['year'], player[key]['week'], player[key]['time'], player[key]['day'], player[key]['game_id'], \
                        key, player[key]['player_id']['player_id'], player[key]['player_id']['name'], player[key]['name'], player[key]['player_id']['pos'], \
                        player[key]['team'], home_away, opp, score, opp_score, \
                        player[key]['pass_cmp'], player[key]['pass_att'], player[key]['pass_yds'], player[key]['pass_tds'], player[key]['ints'], \
                        player[key]['pass_twopta'], player[key]['pass_twoptm'], player[key]['rush_att'], player[key]['rush_yds'], player[key]['rush_tds'], \
                        player[key]['rush_lng'], player[key]['rush_lngtd'], player[key]['rush_twopta'], player[key]['rush_twoptm'], player[key]['rec'], \
                        player[key]['rec_yds'], player[key]['rec_tds'], player[key]['rec_lng'], player[key]['rec_lngtd'], player[key]['rec_twopta'], \
                        player[key]['rec_twoptm'], player[key]['fumbles_lost'], dkp, fdp, player[key]['player_id']['url'])
                        
            x = con.cursor()
            x.execute(query)
    
    print "gamelist inserted into table"
    return


playerIDdict = openplayerdict()
gamelist = []
# year = 2014
# for week in Weeks[:2]:
#     for i in range(0,2):
#         # week = 1
#         # year = 2015
#         dateinfo = [week, year]
#         gameid = getgameids(dateinfo[0], dateinfo[1])[i]
#         getgamedata(gameid, dateinfo, playerIDdict, gamelist)
#     print year, ": week ", week, " complete"
#     time.sleep(2)


for year in Years:
    for week in Weeks:
        dateinfo = [week, year]
        for gameid in getgameids(dateinfo[0], dateinfo[1]):
            print gameid
            getgamedata(gameid, dateinfo, playerIDdict, gamelist)       #### Returns gamelist
            # tableinsert(gamelist)
        print year, ": week ", week, " complete"
        time.sleep(1)

saveplayerdict(playerIDdict)


tableinsert(gamelist)


