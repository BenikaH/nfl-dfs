import requests


r = requests.get("http://www.pinnaclesports.com/webapi/1.14/api/v1/GuestLines/NonLive/15/889").json()

print r["Leagues"][0]["Events"][0].keys()
print r["Leagues"][0]["Events"][1]["Participants"][0]