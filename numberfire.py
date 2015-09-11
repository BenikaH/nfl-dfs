#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import MySQLdb

f = open('nfl-dfs/weekinfo.txt', 'r')
# f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])

r = requests.get("http://www.numberfire.com/nfl/fantasy/fantasy-football-projections").text
soup = BeautifulSoup(r)

# weekNum = int(raw_input("Week number? "))

projData = soup.find_all("tbody", {"id" : "projection-data"})


player = []
playerList = []

playerSet = projData[0].find_all("tr")

for players in playerSet:
    player.append(weekNum)
    try:
        links = players.find("a")   # Add player ID
        plLink = links.get("rel")[0]
        plLink = int(plLink)
        player.append(plLink)
    except:
        player.append(0)
    rows = players.find_all("td")
    for row in rows:
        item = row.text.strip()
        item = item.replace('$','').replace('#','')
        player.append(item)
    playerinfo = player[2].split('(')
    firstname = playerinfo[0].split(' ',1)[0]
    lastname = playerinfo[0].split(' ',1)[1].strip()
    pos = playerinfo[1].split(',')[0]
    team = playerinfo[1].split(',')[1][:-1]
    player.append(firstname)
    player.append(lastname)
    player.append(pos)
    player.append(team)
    playerList.append(player)
    player = []

print playerList[:2]


headerList = ['week','player_id','player','opp','opp_rank','ovr_rank','pos_rank','pass_yds','pass_td','INTs','rush_att','rush_yds','rush_td','rec','rec_yds','rec_td',\
'numberfire_proj','sal_sep1','sal_sep2','sal_sep3','fd_salary','fdp','fd_value','dk_salary','dkp','dk_value',\
'ff_sal','ff_proj','ff_value','dd_sal','dd_proj','dd_value','fa_sal','fa_proj','fa_value','draftster_sal','draftster_proj','draftster_value',\
'fs_sal','fs_proj','fs_value','victiv_sal','victiv_proj','victiv_value',\
'yahoo_sal','yahoo_proj','yahoo_value','firstname','lastname','pos','team']

"""
[1, 10, u'Aaron Rodgers (QB, GB)', u'CHI', u'29', u'1',\
 u'1', u'281.45', u'2.32', u'0.57', u'2.71', u'14.16', u'0.22', u'0.00', u'0.00', u'0.00', \
 u'21.86', u'', u'', u'', u'22.42', u'9700', u'2.31', u'22.6', u'8600', u'2.63', \
 u'21.85', u'0', u'0', u'22.42', u'0', u'0', u'24.67', u'7450', u'3.31', \
 u'22.6', u'0', u'0', u'25.6', u'8800', u'2.91', u'22.6', \
 u'8300', u'2.72', u'Aaron', u'Rodgers ', u'QB', u' GB']
"""


# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')

query = "DELETE FROM numberfire_wkly_proj WHERE week = %d" % (weekNum)
x = con.cursor()
x.execute(query)

for row in playerList:
    print row
    with con:
        
        query = "INSERT INTO numberfire_wkly_proj (week, player_id, playernm_full, opp, opp_rank, ovr_rank, \
                pos_rank, pass_yds, pass_td, ints, rush_att, rush_yds, rush_td, rec, rec_yds, rec_td, \
                numberfire_proj, sal_sep1, sal_sep2, sal_sep3, fdp, fd_salary, fd_value, dkp, dk_salary, dk_value, \
                ff_proj, ff_salary, ff_value, dd_proj, dd_salary, dd_value, fa_proj, fa_salary, fa_value, \
                draftster_proj, draftster_salary, draftster_value, fs_proj, fs_salary, fs_value, victiv_proj, \
                victiv_salary, victiv_value, yahoo_proj, yahoo_salary, yahoo_value, playernm_first, playernm_last, pos, team) \
                VALUES (%d, %d, "'"%s"'", "'"%s"'", %d, %d, \
                %d, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, %1.2f, \
                %1.2f, "'"%s"'", "'"%s"'", "'"%s"'", %1.2f, %d, %1.2f, %1.2f, %d, %1.2f, \
                %1.2f, %d, %1.2f, %1.2f, %d, %1.2f, %1.2f, %d, %1.2f, \
                %1.2f, %d, %1.2f, %1.2f, %d, %1.2f, %1.2f, \
                %d, %1.2f, %1.2f, %d, %1.2f, "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (weekNum, row[1], row[2], row[3], int(row[4]), int(row[5]), \
                int(row[6]), round(float(row[7]),2), round(float(row[8]),2), round(float(row[9]),2), round(float(row[10]),2), round(float(row[11]),2), round(float(row[12]),2), round(float(row[13]),2), round(float(row[14]),2), round(float(row[15]),2), \
                round(float(row[16]),2), row[17], row[18], row[19], round(float(row[20]),2), int(row[21]), round(float(row[22]),2), round(float(row[23]),2), int(row[24]), round(float(row[25]),2), \
                round(float(row[26]),2), int(row[27]), round(float(row[28]),2), round(float(row[29]),2), int(row[30]), round(float(row[31]),2), round(float(row[32]),2), int(row[33]), round(float(row[34]),2), \
                round(float(row[35]),2), int(row[36]), round(float(row[37]),2), round(float(row[38]),2), int(row[39]), round(float(row[40]),2), round(float(row[41]),2), \
                int(row[42]), round(float(row[43]),2), round(float(row[44]),2), int(row[45]), round(float(row[46]),2), row[47], row[48], row[49], row[50])
                
        x = con.cursor()
        x.execute(query)