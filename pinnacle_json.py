#!/usr/local/bin/python2.7

import requests
import MySQLdb

r = requests.get("http://www.pinnaclesports.com/webapi/1.14/api/v1/GuestLines/NonLive/15/889").json()

# 880 -- College Football, 889 -- NFL

f = open('nfl-dfs/weekinfo.txt', 'r')
# f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')

# See if there is data in the table - if there is not, they are opening lines
with con:

# bring in past results
    cur = con.cursor()
    cur.execute("SELECT * FROM pinnacle_odds WHERE week = %d" % (weekNum))

    rows = cur.fetchall()
    if len(rows) > 0:
        firstPull = False
    else:
        firstPull = True
        
# firstPull = True

events = r["Leagues"][0]["Events"]
game = []
gameList = []
for event in events:

    if event['Totals'] and event['PeriodNumber'] == 0:      ### Only get Full Game Line (fix this later!)
        total = float(event['Totals']['Min'])
        
        print '\n', event['EventId']
        print 'Over Price', event['Totals']['OverPrice']
        print 'Under Price', event['Totals']['UnderPrice']
        print 'Total', event['Totals']['Min']
        
        game.append(event['EventId'])
        game.append(event['Totals']['OverPrice'])
        game.append(event['Totals']['UnderPrice'])
        game.append(event['Totals']['Min'])
        
        for participants in event['Participants']:
            spread = float(participants['Handicap']['Min'])
            teamTotal = ((total/2)-(spread/2))
            game.append(participants['Name'])
            game.append(participants['MoneyLine'])
            game.append(participants['Handicap']['Min'])
            game.append(participants['Handicap']['Price'])
            game.append(teamTotal)
            print 'Name', participants['Name']
            print 'ML', participants['MoneyLine']
            print 'Spread', participants['Handicap']['Min']
            print 'Odds', participants['Handicap']['Price']
            print teamTotal
        gameList.append(game)
        print game
    game = []

hmorder = [9,4,10,11,12,13,5,6,7,8,1,2,3,0]
aworder = [4,9,5,6,7,8,10,11,12,13,1,2,3,0]

headers = ['team', 'opp', 'home_away', 'team_ml', 'team_spread', 'team_odds', 'team_total', 'opp_ml', 'opp_spread' \
            'opp_odds', 'opp_total', 'overprice', 'underprice', 'total']
holder = []
gameinfo = []

for game in gameList:
    holder = [game[i] for i in hmorder]  # List method to put items into home team order
    holder.insert(0, weekNum)
    holder.insert(3, 'Home')             # Add 'Home' to home teams
    gameinfo.append(holder)
    holder = [game[i] for i in aworder]  # List method to put items into away team order
    holder.insert(0, weekNum)
    holder.insert(3, 'Away')             # Add 'Away' to away teams
    print holder
    gameinfo.append(holder)

# If this isn't the first run, calculate the change and insert into the list
if not firstPull:
    holder = []
    pastresults = []
    for row in rows:
        for item in row:
            holder.append(item)
        pastresults.append(holder)
        holder = []
    
    for game in gameinfo:
        for i in range(0,6):
            game.insert(15, 0.00)
        for past in pastresults:
            if game[1] == past[2] and game[2] == past[3]:
                print past
                game[15] = past[16]      # teamtotal_open
                game[16] = past[17]      # spread_open
                game[17] = past[18]      # total_open
                game[18] = float(game[7]) - float(game[15])      # teamtotal_chg
                game[19] = float(game[5]) - float(game[16])      # spread_chg
                game[20] = float(game[14]) - float(game[17])      # total_chg

# If this is the first run, insert in placeholders and make the opening lines set to the current lines
else:
    for game in gameinfo:
        for i in range(0,6):
            game.insert(15, 0.00)
        game[15] = game[7] 
        game[16] = game[5]
        game[17] = game[14]

print gameinfo

####### Add to database

query = "DELETE FROM pinnacle_odds WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in gameinfo:
    # print row
    with con:
        query = "INSERT INTO pinnacle_odds (week, team, opp, home_away, ml, spread, odds, teamtotal, \
                opp_ml, opp_spread, opp_odds, opp_total, over_price, under_price, total, teamtotal_open, \
                spread_open, total_open, teamtotal_chg, spread_chg, total_chg, game_id) \
                VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                        "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], \
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], \
            row[19], row[20], row[21])
        x = con.cursor()
        x.execute(query)