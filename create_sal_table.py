#!/usr/local/bin/python2.7

import MySQLdb
import csv

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')


f = open('nfl-dfs/weekinfo.txt', 'r')
# f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])

curWeek = 'week' + str(weekNum)
if weekNum == 1:
    prvWeek = curWeek
else:
    prvWeek = 'week' + str(weekNum - 1)

with con:
    query = "DELETE FROM weekly_salaries_dk;"
    x = con.cursor()
    x.execute(query)


with con:
    query = "INSERT INTO weekly_salaries_dk (player_id,playernm_full,week1_sal,week2_sal,week3_sal,week4_sal,\
    week5_sal,week6_sal,week7_sal,week8_sal,week9_sal,week10_sal,week11_sal,week12_sal,week13_sal,week14_sal,\
    week15_sal,week16_sal,week17_sal,week_chg,season_chg)\
    (\
    SELECT\
    player_id,\
    playernm_full,\
    sum(week1) as week1_sal,\
    sum(week2) as week2_sal,\
    sum(week3) as week3_sal,\
    sum(week4) as week4_sal,\
    sum(week5) as week5_sal,\
    sum(week6) as week6_sal,\
    sum(week7) as week7_sal,\
    sum(week8) as week8_sal,\
    sum(week9) as week9_sal,\
    sum(week10) as week10_sal,\
    sum(week11) as week11_sal,\
    sum(week12) as week12_sal,\
    sum(week13) as week13_sal,\
    sum(week14) as week14_sal,\
    sum(week15) as week15_sal,\
    sum(week16) as week16_sal,\
    sum(week17) as week17_sal,\
    case when sum(%s) = 0 then 0 else sum(%s) - sum(%s) end as week_chg,\
    sum(%s) - sum(week1) as season_chg\
    FROM\
    (SELECT player_id, \
    playernm_full, \
    case when week = 1 then dk_salary else 0 end as week1,\
    case when week = 2 then dk_salary else 0 end as week2,\
    case when week = 3 then dk_salary else 0 end as week3,\
    case when week = 4 then dk_salary else 0 end as week4,\
    case when week = 5 then dk_salary else 0 end as week5,\
    case when week = 6 then dk_salary else 0 end as week6,\
    case when week = 7 then dk_salary else 0 end as week7,\
    case when week = 8 then dk_salary else 0 end as week8,\
    case when week = 9 then dk_salary else 0 end as week9,\
    case when week = 10 then dk_salary else 0 end as week10,\
    case when week = 11 then dk_salary else 0 end as week11,\
    case when week = 12 then dk_salary else 0 end as week12,\
    case when week = 13 then dk_salary else 0 end as week13,\
    case when week = 14 then dk_salary else 0 end as week14,\
    case when week = 15 then dk_salary else 0 end as week15,\
    case when week = 16 then dk_salary else 0 end as week16,\
    case when week = 17 then dk_salary else 0 end as week17\
    from numberfire_wkly_proj) sal\
    GROUP BY 1,2\
    ORDER BY week1_sal desc);" % (prvWeek, curWeek, prvWeek, curWeek)
    x = con.cursor()
    x.execute(query)
    
##### Fanduel Salaries
with con:
    query = "DELETE FROM weekly_salaries_fd;"
    x = con.cursor()
    x.execute(query)


with con:
    query = "INSERT INTO weekly_salaries_fd (player_id,playernm_full,week1_sal,week2_sal,week3_sal,week4_sal,\
    week5_sal,week6_sal,week7_sal,week8_sal,week9_sal,week10_sal,week11_sal,week12_sal,week13_sal,week14_sal,\
    week15_sal,week16_sal,week17_sal,week_chg,season_chg)\
    (\
    SELECT\
    player_id,\
    playernm_full,\
    sum(week1) as week1_sal,\
    sum(week2) as week2_sal,\
    sum(week3) as week3_sal,\
    sum(week4) as week4_sal,\
    sum(week5) as week5_sal,\
    sum(week6) as week6_sal,\
    sum(week7) as week7_sal,\
    sum(week8) as week8_sal,\
    sum(week9) as week9_sal,\
    sum(week10) as week10_sal,\
    sum(week11) as week11_sal,\
    sum(week12) as week12_sal,\
    sum(week13) as week13_sal,\
    sum(week14) as week14_sal,\
    sum(week15) as week15_sal,\
    sum(week16) as week16_sal,\
    sum(week17) as week17_sal,\
    case when sum(%s) = 0 then 0 else sum(%s) - sum(%s) end as week_chg,\
    sum(%s) - sum(week1) as season_chg\
    FROM\
    (SELECT player_id, \
    playernm_full, \
    case when week = 1 then fd_salary else 0 end as week1,\
    case when week = 2 then fd_salary else 0 end as week2,\
    case when week = 3 then fd_salary else 0 end as week3,\
    case when week = 4 then fd_salary else 0 end as week4,\
    case when week = 5 then fd_salary else 0 end as week5,\
    case when week = 6 then fd_salary else 0 end as week6,\
    case when week = 7 then fd_salary else 0 end as week7,\
    case when week = 8 then fd_salary else 0 end as week8,\
    case when week = 9 then fd_salary else 0 end as week9,\
    case when week = 10 then fd_salary else 0 end as week10,\
    case when week = 11 then fd_salary else 0 end as week11,\
    case when week = 12 then fd_salary else 0 end as week12,\
    case when week = 13 then fd_salary else 0 end as week13,\
    case when week = 14 then fd_salary else 0 end as week14,\
    case when week = 15 then fd_salary else 0 end as week15,\
    case when week = 16 then fd_salary else 0 end as week16,\
    case when week = 17 then fd_salary else 0 end as week17\
    from numberfire_wkly_proj) sal\
    GROUP BY 1,2\
    ORDER BY week1_sal desc);" % (prvWeek, curWeek, prvWeek, curWeek)
    x = con.cursor()
    x.execute(query)
#
with con:
    query = "SELECT * FROM weekly_salaries_dk;"
    x = con.cursor()
    x.execute(query)
    rows = x.fetchall()
    fp = open('week1sal.csv', 'w')
    myFile = csv.writer(fp)
    myFile.writerows(rows)
    print rows
    fp.close()
#
# player = []
# playerList = []
# for row in rows:
#     print row


