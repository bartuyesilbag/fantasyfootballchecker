# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

global suspendedAndInjuredPlayers
suspendedAndInjuredPlayers = dict()

def getList(soup, playerDict):
    odds = soup.find_all('tr', attrs={ 'class' : 'odd'})
    evens = soup.find_all('tr', attrs={ 'class' : 'even'})

    for odd in odds:
        playerName = unidecode(odd.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        playerTeam = unidecode(odd.find('td', attrs={ 'class' : 'zentriert no-border-rechts'}).a.attrs['title'])
        if 'U21' in playerTeam:
            continue
        if playerTeam not in playerDict:
            playerDict[playerTeam] = []
        playerDict[playerTeam].append(playerName)

    for even in evens:
        playerName = unidecode(even.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        playerTeam = unidecode(even.find('td', attrs={ 'class' : 'zentriert no-border-rechts'}).a.attrs['title'])
        if 'U21' in playerTeam:
            continue
        if playerTeam not in playerDict:
            playerDict[playerTeam] = []
        playerDict[playerTeam].append(playerName)

def getCleanSheetPlayerStats(soup):
    odds = soup.find_all('tr', attrs={ 'class' : 'odd'})
    evens = soup.find_all('tr', attrs={ 'class' : 'even'})
    cleanSheetDict = dict()
    for odd in odds:
        playerName = unidecode(odd.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        cleanSheetMatchNumber = unidecode(odd.find_all('td', attrs={ 'class' : 'zentriert'})[-2].text)
        cleanSheetDict[playerName] = int(cleanSheetMatchNumber)

    for even in evens:
        playerName = unidecode(even.find('td', attrs={ 'class' : 'hauptlink'}).text.replace('\n', ''))
        cleanSheetMatchNumber = unidecode(even.find_all('td', attrs={ 'class' : 'zentriert'})[-2].text)
        
        cleanSheetDict[playerName] = int(cleanSheetMatchNumber)

    return dict(sorted(cleanSheetDict.items(), key=lambda item: item[1], reverse = True))

def getCleanSheetPlayers():
    super_league = 'https://www.transfermarkt.com/super-lig/weisseweste/wettbewerb/TR1'
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(super_league, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return getCleanSheetPlayerStats(soup)

def getSuspendedPlayersInfo():
    premiere_league = 'https://www.transfermarkt.com.tr/premier-league/verletztespieler/wettbewerb/GB1'
    super_league = 'https://www.transfermarkt.com/super-lig/sperrenausfaelle/wettbewerb/TR1'
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(super_league, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    getList(soup, suspendedAndInjuredPlayers)    
    
    if soup.find('div', attrs={ 'class' : 'pager'}):
        second_page = "https://www.transfermarkt.com/super-lig/sperrenausfaelle/wettbewerb/TR1/page/2"
        response = requests.get(second_page, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        getList(soup.find('table', attrs={ 'class' : 'items'}), suspendedAndInjuredPlayers)
    return True

def getInjuredPlayersInfo():
    premiere_league = 'https://www.transfermarkt.com.tr/premier-league/verletztespieler/wettbewerb/GB1'
    super_league = 'http://www.transfermarkt.com.tr/super-lig/verletztespieler/wettbewerb/TR1'
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(super_league, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    getList(soup, suspendedAndInjuredPlayers)
    
    return True

def main():
    getInjuredPlayersInfo()
    getSuspendedPlayersInfo()
    cleanSheetPlayers = getCleanSheetPlayers()

    suspendedPlayersJSON = json.dumps(suspendedAndInjuredPlayers, indent=4, ensure_ascii=False, sort_keys=True)
    cleanSheetPlayersJSON = json.dumps(cleanSheetPlayers, indent=4, ensure_ascii=False)
    print(cleanSheetPlayersJSON)



if __name__ == "__main__":
    main()
