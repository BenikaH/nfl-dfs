#!/usr/local/bin/python2.7

import MySQLdb
import csv
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart

# con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')

f = open('nfl-dfs/weekinfo.txt', 'r')
# f = open('weekinfo.txt', 'r')             ### Local
ftext = f.read().split(',')
weekNum = int(ftext[0])
send = ftext[1]
print send
f.close()
    
with con:
    query = 'SELECT nf.week,\
    rgo.game_date,\
    concat(nf.playernm_first, " ", nf.playernm_last) as playernm_full,\
    nf.pos,\
    nf.team,\
    nf.opp,\
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
    fs.dkp as fs_dkp,\
    fs.fdp as fs_fdp,\
    e.dkp as e_dkp,\
    e.fdp as e_fdp,\
    c.dkp as c_dkp,\
    c.fdp as c_fdp,\
    rgo.team_spread,\
    rgo.total_pts,\
    rgo.team_proj,\
    rgo.team_proj_chg,\
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
    LEFT JOIN rotowire_wkly_proj rw on rw.player_id = map.rotowire_id and rw.week = %d\
    LEFT JOIN rotogrinders_wkly_proj rg on rg.player_id = map.rotogrinders_id and rg.week = %d\
    LEFT JOIN fantasypros_wkly_proj fp on fp.player_id = map.fantasypros_id and fp.week = %d\
    LEFT JOIN foxsports_wkly_proj fs on fs.player_id = map.foxsports_id and fs.week = %d\
    LEFT JOIN espn_wkly_proj e on e.player_id = map.espn_id and e.week = %d\
    LEFT JOIN cbssports_wkly_proj c on c.player_id = map.cbssports_id and c.week = %d\
    LEFT JOIN team_map tm on nf.team = tm.nf_team\
    LEFT JOIN rotogrinders_odds rgo on rgo.team = tm.rg_team\
    LEFT JOIN weekly_salaries_dk dks on dks.player_id = nf.player_id\
    LEFT JOIN weekly_salaries_fd fds on fds.player_id = nf.player_id\
    LEFT JOIN (select dk_salary, sum(points)/sum(players) as avg_dkp from v_dk_salary_stats group by 1) vdk on vdk.dk_salary = nf.dk_salary\
    LEFT JOIN (select fd_salary, sum(points)/sum(players) as avg_fdp from v_fd_salary_stats group by 1) vfd on vfd.fd_salary = nf.fd_salary\
    LEFT JOIN (select distinct player_id from dfs_results_2014) guru on guru.player_id= map.rotoguru_id\
    LEFT JOIN consistency_tiers cons on cons.player_id = guru.player_id\
    \
    WHERE nf.week = %d\
    ORDER BY nf.dk_salary DESC;' % (weekNum, weekNum, weekNum, weekNum, weekNum, weekNum, weekNum)
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
    msg['From'] = 'Ryan.Murray4@gmail.com'
    msg['To'] = 'Ryan.Murray4@gmail.com'

    me = msg['From']
    you = msg['To']

    # Send the message via our own SMTP server, but don't include the

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.login("Ryan.Murray4@gmail.com", "Syracuse#44")
 
    server.sendmail(msg['From'], msg['To'] , msg.as_string())
    server.close()

