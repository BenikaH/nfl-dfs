#!/usr/local/bin/python2.7

import MySQLdb
import csv
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart

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
    local = False
    if local == False:
        fldr = 'nfl-dfs/'
        serverinfo = security('mysql', fldr)
        con = MySQLdb.connect(host='mysql.server', user=serverinfo[0], passwd=serverinfo[1], db='MurrDogg4$dfs-nfl')
    else:
        fldr = ''
        con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection

    f = open(fldr + 'weekinfo.txt', 'r')
    ftext = f.read().split(',')
    # weekNum = int(ftext[0])
    send = ftext[1]
    print send
    f.close()

    weekNum = getweek()

    if send == "Send":
        f = open(fldr + 'inputfile.txt', 'r')
        ftext = f.read().split(',')
        email = ftext[0]
        pwd = ftext[1]
        f.close()
    
    with con:
        query = 'SELECT nf.week,\
        p.gamedate,\
        concat(nf.playernm_first, " ", nf.playernm_last) as playernm_full,\
        nf.pos,\
        nf.team,\
        nf.opp,\
        rg.playernm_full,\
        nf.dk_salary,\
        dks.week_chg,\
        nf.fd_salary,\
        fds.week_chg,\
        nf.opp_rank,\
        nf.ovr_rank,\
        nf.pos_rank,\
        nf.dkp as nf_dkp,\
        nf.fdp as nf_fdp,\
        rw.dkp as rw_dkp,\
        rw.fdp as rw_fdp,\
        rg.dkp as rg_dkp,\
        rg.fdp as rg_fdp,\
        fp.dkp as fp_dkp,\
        fp.fdp as fp_fdp,\
        e.dkp as e_dkp,\
        e.fdp as e_fdp,\
        c.dkp as c_dkp,\
        c.fdp as c_fdp,\
        fg.av_dkp as fg_dkp,\
        fg.av_fdp as fg_fdp,\
        p.spread,\
        p.total,\
        p.teamtotal,\
        p.spread_chg,\
        p.total_chg,\
        p.teamtotal_chg,\
        p.consensus,\
        vdk.avg_dkp,\
        vfd.avg_fdp,\
        cons.toptier_dk,\
        cons.midtier_dk,\
        cons.lowtier_dk,\
        cons.toptier_fd,\
        cons.midtier_fd,\
        cons.lowtier_fd\
        FROM\
        numberfire_wkly_proj nf\
        LEFT JOIN player_map map on nf.player_id = map.numberfire_id\
        LEFT JOIN (select distinct player_id, week, dkp, fdp from rotowire_wkly_proj) rw on rw.player_id = map.rotowire_id and rw.week = %d\
        LEFT JOIN rotogrinders_wkly_proj rg on rg.player_id = map.rotogrinders_id and rg.week = %d\
        LEFT JOIN fantasypros_wkly_proj fp on fp.player_id = map.fantasypros_id and fp.week = %d\
        LEFT JOIN espn_wkly_proj e on e.player_id = map.espn_id and e.week = %d\
        LEFT JOIN cbssports_wkly_proj c on c.player_id = map.cbssports_id and c.week = %d\
        LEFT JOIN footballguys_wkly_proj fg on fg.playernm_full = map.footballguys_id and fg.week = %d\
        LEFT JOIN team_map tm on nf.team = tm.nf_team\
        LEFT JOIN rotogrinders_odds rgo on rgo.team = tm.rg_team and rgo.week = %d\
        LEFT JOIN pinnacle_odds p on p.team = tm.pinnacle_team and p.week = %d\
        LEFT JOIN weekly_salaries_dk dks on dks.player_id = nf.player_id\
        LEFT JOIN weekly_salaries_fd fds on fds.player_id = nf.player_id\
        LEFT JOIN (select dk_salary, sum(points)/sum(players) as avg_dkp from v_dk_salary_stats group by 1) vdk on vdk.dk_salary = nf.dk_salary\
        LEFT JOIN (select fd_salary, sum(points)/sum(players) as avg_fdp from v_fd_salary_stats group by 1) vfd on vfd.fd_salary = nf.fd_salary\
        LEFT JOIN (select distinct player_id from v_rotoguru_historicals) guru on guru.player_id= map.rotoguru_id\
        LEFT JOIN (select distinct player_id, toptier_dk, midtier_dk, lowtier_dk, toptier_fd, midtier_fd, lowtier_fd from consistency_tiers) cons on cons.player_id = guru.player_id\
        \
        WHERE nf.week = %d\
        ORDER BY nf.dk_salary DESC;' % (weekNum, weekNum, weekNum, weekNum, weekNum, weekNum, weekNum, weekNum, weekNum)
        x = con.cursor()
        x.execute(query)

    rows = x.fetchall()
    fp = open('week' + str(weekNum) +'output.csv', 'w')
    myFile = csv.writer(fp)
    myFile.writerows(rows)
    fp.close()

    if send == "Send":
        msg = MIMEMultipart()
        f = file('week'+str(weekNum)+'output.csv')
        attachment = MIMEText(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename='week' + str(weekNum) +'output.csv')
        msg.attach(attachment)
        # Create a text/plain message


        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = 'Week ' + str(weekNum) + ' Output File'
        msg['From'] = email
        msg['To'] = email

        me = msg['From']
        you = msg['To']

        # Send the message via our own SMTP server, but don't include the

        server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        server.login(email, pwd)
 
        server.sendmail(msg['From'], msg['To'] , msg.as_string())
        server.close()




    # counter = 1
    # >>> for w in sorted(playerlist, key=lambda x:x['score']):
    # ...   w['scorerank'] = counter/(1.0 * len(playerlist))
    # ...   counter += 1
    # ...
    # >>> playerlist
    # [{'ptsrank': 0.6666666666666666, 'score': 90, 'pts': 25.4, 'name': 'Rodgers', 'scorerank': 0.3333333333333333}, {'ptsrank': 1.0, 'score': 92.4, 'pts': 30.9, 'name': 'Brady', 'scorerank': 1.0}, {'ptsrank': 0.3333333333333333, 'score': 91, 'pts': 24.9, 'name': 'Tebow', 'scorerank': 0.6666666666666666}]
    
    return
    
if __name__ == '__main__':
    main()
