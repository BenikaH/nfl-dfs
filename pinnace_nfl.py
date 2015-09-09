from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import csv

daysList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

driver = webdriver.Chrome()

driver.get("http://www.pinnaclesports.com/en/odds/match/football/usa/nfl?sport=True")

html = driver.page_source

soup = BeautifulSoup(html)

table = soup.find_all("tbody", {"class": "ng-scope"}) # Get tables with all the odds data
game = []
gameList = []
for games in table:
    rows = games.find_all("span", {"class": "ng-binding"})
    for row in rows:
        item = row.text.strip()
        print item
        game.append(item)
    gameList.append(game)
    game = []
    
print gameList

driver.quit()
