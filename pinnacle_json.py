#!/usr/local/bin/python2.7

import requests
import MySQLdb


def getData():
    
    r = requests.get("http://www.pinnaclesports.com/webapi/1.14/api/v1/GuestLines/NonLive/15/889").json()
    # 880 -- College Football, 889 -- NFL
    
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

            gamedate = event['DateAndTime'][:10]
            gametime = event['DateAndTime'][11:-1]        
            game.append(event['EventId'])
            game.append(gamedate)
            game.append(gametime)
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
    return gameList


def homeawaySplit(gameList, weekNum):
    
    hmorder = [11,6,12,13,14,15,7,8,9,10,3,4,5,0,1,2]
    aworder = [6,11,7,8,9,10,12,13,14,15,3,4,5,0,1,2]


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
    
    return gameinfo

def linemovement(con, gameinfo, weekNum):
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
    
    # If this is the first run, insert in placeholders and make the opening lines set to the current lines
    if firstPull:
        for game in gameinfo:
            for i in range(0,6):
                game.insert(15, 0.00)
            game[15] = game[7] 
            game[16] = game[5]
            game[17] = game[14]

    # If this isn't the first run, calculate the change and insert into the list
    else:
        holder = []
        pastresults = []
        for row in rows:
            for item in row[1:]:            # All items except primary key ID
                holder.append(item)
            pastresults.append(holder)
            holder = []
        print "\n\n", pastresults, "\n\n"
        
        for game in gameinfo:
            for i in range(0,6):
                game.insert(15, 0.00)
                
        for past in pastresults:
            for game in gameinfo:
                if past[1] == game[1] and past[2] == game[2]:
                    print past
                    # game[15] = past[16]      # teamtotal_open
                    # game[16] = past[17]      # spread_open
                    # game[17] = past[18]      # total_open
                    print past[1], float(game[7]), float(past[15])
                    past[18] = float(game[7]) - float(past[15])      # teamtotal_chg
                    past[19] = float(game[5]) - float(past[16])      # spread_chg
                    past[20] = float(game[14]) - float(past[17])      # total_chg
    
        gameinfo = pastresults
        
    return gameinfo

def addtoDb(con, gameinfo, weekNum):          ####### Add to database

    query = "DELETE FROM pinnacle_odds WHERE week = %d" % (weekNum)
    x = con.cursor()
    x.execute(query)

    for row in gameinfo:
        # print row
        with con:
            query = "INSERT INTO pinnacle_odds (week, team, opp, home_away, ml, spread, odds, teamtotal, \
                    opp_ml, opp_spread, opp_odds, opp_total, over_price, under_price, total, teamtotal_open, \
                    spread_open, total_open, teamtotal_chg, spread_chg, total_chg, game_id, gamedate, gametime) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], \
                row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], \
                row[19], row[20], row[21], row[22], row[23])
            x = con.cursor()
            x.execute(query)
    return

def main():


    headers = ['team', 'opp', 'home_away', 'team_ml', 'team_spread', 'team_odds', 'team_total', 'opp_ml', 'opp_spread' \
                'opp_odds', 'opp_total', 'overprice', 'underprice', 'total', 'gamedate', 'gametime']

    ##### Get week number
    f = open('nfl-dfs/weekinfo.txt', 'r')
    # f = open('weekinfo.txt', 'r')             ### Local
    ftext = f.read().split(',')
    weekNum = int(ftext[0])

    # con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
    con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
    gameList = getData()
    gameinfo = linemovement(con, homeawaySplit(gameList, weekNum), weekNum)
    addtoDb(con, gameinfo, weekNum)
    
if __name__ == '__main__':
    main()