# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

injuredPlayers = dict()
suspendedPlayers = dict()



def getList(soup, playerDict):
    odds = soup.find_all('tr', attrs={ 'class' : 'odd'})
    evens = soup.find_all('tr', attrs={ 'class' : 'even'})

    for odd in odds:
        playerName = unidecode(odd.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        playerTeam = unidecode(odd.find('td', attrs={ 'class' : 'zentriert no-border-rechts'}).a.attrs['title'])
        if playerTeam not in playerDict:
            playerDict[playerTeam] = []
        playerDict[playerTeam].append(playerName)

    for even in evens:
        playerName = unidecode(even.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        playerTeam = unidecode(even.find('td', attrs={ 'class' : 'zentriert no-border-rechts'}).a.attrs['title'])
        if playerTeam not in playerDict:
            playerDict[playerTeam] = []
        playerDict[playerTeam].append(playerName)


def getSuspendedPlayersInfo():
    premiere_league = 'https://www.transfermarkt.com.tr/premier-league/verletztespieler/wettbewerb/GB1'
    super_league = 'https://www.transfermarkt.com/super-lig/sperrenausfaelle/wettbewerb/TR1'
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(super_league, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    getList(soup, suspendedPlayers)    
    
    if soup.find('div', attrs={ 'class' : 'pager'}):
        second_page = "https://www.transfermarkt.com/super-lig/sperrenausfaelle/wettbewerb/TR1/page/2"
        response = requests.get(second_page, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        getList(soup.find('table', attrs={ 'class' : 'items'}), suspendedPlayers)
    return True


def getInjuredPlayersInfo():
    premiere_league = 'https://www.transfermarkt.com.tr/premier-league/verletztespieler/wettbewerb/GB1'
    super_league = 'http://www.transfermarkt.com.tr/super-lig/verletztespieler/wettbewerb/TR1'
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(super_league, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    getList(soup, injuredPlayers)
    
    return True

def main():
    getInjuredPlayersInfo()
    getSuspendedPlayersInfo()
    injuredPlayersJSON = json.dumps(injuredPlayers, indent=4, ensure_ascii=False, sort_keys=True)
    suspendedPlayersJSON = json.dumps(suspendedPlayers, indent=4, ensure_ascii=False, sort_keys=True)
    print("*Injured Players*")
    print(injuredPlayersJSON)
    print("*Suspended Players*")
    print(suspendedPlayersJSON)

if __name__ == "__main__":
    main()
