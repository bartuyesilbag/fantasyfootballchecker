# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from telegram.ext import *

API_KEY = ''


global suspendedPlayers
suspendedPlayers = dict()

global injuredPlayers
injuredPlayers = dict()


def startCommand(update, context):
    update.message.reply_text(text= f"*Merhaba {update.effective_user.first_name}, sakat , cezali veya cleansheet yazarak baslayabilirsin...*", parse_mode= 'Markdown')

def helpCommand(update, context):
    update.message.reply_text('sakat , cezali veya cleansheet yazarak baslayabilirsin...', parse_mode= 'Markdown')

def handleMessage(update, context):
    text = str(update.message.text).lower()
    response = responses(text)

    update.message.reply_text(response, parse_mode= 'Markdown')


def error(update, context):
    print(f"Update {update} caused error {context.error}")




def responses(inputText):
    userMessage = str(inputText).lower()
    
    if userMessage in ('sakat', 'sakatlar'):
        getInjuredPlayersInfo()
        ret = "*Sakat Oyuncular:\n*\n"
        for team in injuredPlayers:
            ret += f"*\n{team}:* \n"
            for player in injuredPlayers[team]:
                ret += f"{player}\n"
                
        injuredPlayers.clear()
        return ret
        #return json.dumps(injuredPlayers, indent=4, ensure_ascii=False, sort_keys=True)
    
    if userMessage in ('cezali', 'ceza'):
        getSuspendedPlayersInfo()
        ret = "*Cezalı Oyuncular:\n*\n"
        for team in suspendedPlayers:
            ret += f"*\n{team}:* \n"
            for player in suspendedPlayers[team]:
                ret += f"{player}\n"
                
        suspendedPlayers.clear()
        return ret
        #eturn json.dumps(suspendedPlayers, indent=4, ensure_ascii=False, sort_keys=True)
    
    if userMessage in ('kaleci', 'clean sheet', 'cleansheet', 'clean'):
        cleanSheetPlayers = getCleanSheetPlayers()
        ret = "*Kalecilerin Clean Sheet Sayıları:\n*\n"
        for player in cleanSheetPlayers:
            ret += f"{player}{cleanSheetPlayers[player]} mac\n"

        return ret
    

    return "Anlamadim..."

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
    print("Bot Started...")
    
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CommandHandler("help", helpCommand))

    dp.add_handler(MessageHandler(Filters.text, handleMessage))

    dp.add_error_handler(error)

    updater.start_polling()





if __name__ == "__main__":
    main()
