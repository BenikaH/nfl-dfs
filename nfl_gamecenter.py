#!/usr/local/bin/python2.7

import requests

r = requests.get("http://www.nfl.com/liveupdate/game-center/2015091000/2015091000_gtd.json")

data = r.json()

hmaway = ['home', 'away']

gameid = '2015091000'

gameinfo = data[gameid]

for team in hmaway:
    rushinginfo = gameinfo[team]["stats"]["rushing"]
    for key in rushinginfo.keys():
        print key, team, rushinginfo[key]["name"], rushinginfo[key]["yds"]

