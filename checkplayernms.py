#!/usr/local/bin/python2.7

import csv


masterlist = []
with open('nflplayerids.csv') as f:
    w = csv.DictReader(f)
    for row in w:
        masterlist.append(row)

print masterlist[1]

playerlist = []
with open('playerlist.csv', 'rU') as f:
    w = csv.DictReader(f)
    for row in w:
        playerlist.append(row)
        
print playerlist[1]

tannehill = playerlist[1]['playernm_full']

playercheck = []
for x in playerlist[:10]:
    playercheck.append(x['playernm_full'])

print playercheck

for names in playercheck:
    lastnm = names.split(,1)[1]
    print names, "\n"
    maxnm = 0
    for players in masterlist:
        counter = 0
        for i in names:
            if i in players['name']:
                counter += 1
        if counter > maxnm:
            maxnm = counter
            suggest = players['name']
            
    print suggest, maxnm