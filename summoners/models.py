from django.db import models
import requests
import configparser
import json
import os
import datetime
import time

API_ROUTINGS = {
        'NA': 'https://na1.api.riotgames.com',
        'LAN': 'https://la1.api.riotgames.com',
        }
API_AMERICAS = 'https://americas.api.riotgames.com'

API_URLS = {
        'GetSummonerByName': '/lol/summoner/v4/summoners/by-name/%s',
        'GetSummonerById': '/lol/summoner/v4/summoners/%s',
        'GetSummonerByPUUID': '/lol/summoner/v4/summoners/by-puuid/%s',
        'GetMatchesByPUUID': '/lol/match/v5/matches/by-puuid/%s/ids',
        'GetMatchByID': '/lol/match/v5/matches/%s',
        'GetAllLeagueEntries': '/lol/league-exp/v4/entries/%s/%s/%s',
        }
CONFIG = "/home/rgarcia/projects/lolstats/lolstats.conf"
SOLODUO_QUEUE = 420
DATA_PATH = "/datos/lolstats/"

MAX_PER_SECOND = 20
MAX_PER_2_MINUTES = 100
countPerSecond = 0
countPer2Minutes = 0
lastSecond = 0
lastMinute = 0

class Summoner(models.Model):
    """Invocador.

    Esta clase guarda, manipula y extrae de la API de Riot
    los datos de los invocadores.
    """
    name = models.CharField(max_length=30)
    summonerid = models.CharField(max_length=63)
    puuid = models.CharField(max_length=78)
    level = models.IntegerField()
    region = models.CharField(max_length=5)
    inserttime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Devuelve la descripcion del objeto."""
        return self.name

    def search_summoner(self, region="LAN"):
        """Busca en la API de Riot el summoner y devuelve su info."""
        config = configparser.ConfigParser()
        config.read(CONFIG)
        if self.name != "":
            url = API_ROUTINGS[region] + API_URLS['GetSummonerByName'] %(self.name,)
        elif self.summonerid != "":
            url = API_ROUTINGS[region] + API_URLS['GetSummonerById'] %(self.summonerid,)
        elif self.puuid != "":
            url = API_ROUTINGS[region] + API_URLS['GetSummonerByPUUID'] %(self.puuid)
        else:
            print("No se tienen datos en el invocador")
            return 404

        headers = {
                "X-Riot-Token": config['riot_api']['KEY'],
                }
        response = make_request(url, headers=headers)
        if 200 == response.status_code:
            self.jsondata = response.text
            values = json.loads(self.jsondata)
            self.name = values['name']
            self.summonerid = values['id']
            self.puuid = values['puuid']
            self.level = values['summonerLevel']
            self.region = region
        else:
            print(response.text)
        return response.status_code

    def search_games(self, start=0, count=20):
        """."""
        config = configparser.ConfigParser()
        config.read(CONFIG)
        url = API_AMERICAS + API_URLS['GetMatchesByPUUID'] %(self.puuid,)
        headers = {
                "X-Riot-Token": config['riot_api']['KEY'],
                }
        params = "?queue=%s&start=%s&count=%s" %(SOLODUO_QUEUE, start, count)
        response = make_request(url + params, headers=headers)
        if 200 == response.status_code:
            games = json.loads(response.text)
        else:
            print(response.text)
            games = {}
        return games

    def save_json(self):
        """."""
        filepath = "%s/summoners/%s.json" %(DATA_PATH, self.id)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(self.jsondata)

    def search_summoner_list(queue, tier, division, page=1, region="LAN", ):
        """."""
        config = configparser.ConfigParser()
        config.read(CONFIG)
        url = API_ROUTINGS[region] + API_URLS['GetAllLeagueEntries'] %(queue, tier, division)
        headers = {
                "X-Riot-Token": config['riot_api']['KEY'],
                }
        params = "?page=%s" %(page,)
        #response = requests.get(url + params, headers=headers)
        response = make_request(url + params, headers=headers)
        if 200 == response.status_code:
            entries = json.loads(response.text)
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            filepath = "%s/tiers/%s/%s.json" %(DATA_PATH, region, timestamp)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(response.text)
        else:
            print(response.text)
            entries = {}
        return entries

class Game(models.Model):
    """."""
    gameid = models.CharField(max_length=14)

    def __str__(self):
        """."""
        return self.gameid

    def search_details(self):
        """."""
        config = configparser.ConfigParser()
        config.read(CONFIG)
        url = API_AMERICAS + API_URLS['GetMatchByID'] %(self.gameid,)
        headers = {
                "X-Riot-Token": config['riot_api']['KEY'],
                }
        #response = requests.get(url, headers=headers)
        response = make_request(url, headers=headers)
        if 200 == response.status_code:
            self.jsondata = response.text
            return True
        else:
            print(response.text)
            return False

    def fetch_info(self):
        """."""
        filepath = "%s/games/%s.json" %(DATA_PATH, self.id)
        if os.path.exists(filepath):
            with open(filepath, 'r') as json_file:
                self.jsondata = json.load(json_file)
            return True
        else:
            return False

    def fetch_participants(self):
        """."""
        try:
            result = self.jsondata['info']['participants']
        except KeyError:
            print("Archivo JSON con formato incorrecto")
            result = []
        return result

    def save_json(self):
        """."""
        filepath = "%s/games/%s.json" %(DATA_PATH, self.id)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(self.jsondata)

class GameRecord(models.Model):
    """."""
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    teamid = models.IntegerField()

    def __str__(self):
        """."""
        text = "%s %s" %(self.summoner, self.game)
        return text
    
def make_request(url, headers={}):
    """."""
    global countPerSecond, countPer2Minutes, lastSecond, lastMinute
    while True:
        currentSecond = time.time()
        currentMinute = currentSecond // 60
        if currentSecond == lastSecond:
            if countPerSecond < MAX_PER_SECOND:
                    response = __request(url, headers)
                    if response.status_code == 503:
                        time.sleep(10)
                    else:
                        break
            else:
                time.sleep(1)
        elif abs(currentMinute - lastMinute) <= 2:
            if countPer2Minutes < MAX_PER_2_MINUTES:
                response = __request(url, headers)
                if response.status_code == 503:
                    time.sleep(10)
                else:
                    break
            else:
                time.sleep(1)
        else:
            response = __request(url, headers)
            if response.status_code == 503:
                time.sleep(10)
            else:
                break
    return response

def __request(url, headers):
    global countPerSecond, countPer2Minutes, lastSecond, lastMinute
    countPerSecond += 1
    countPer2Minutes += 1
    response = requests.get(url, headers=headers)
    currentSecond = time.time()
    currentMinute = currentSecond // 60
    if currentSecond != lastSecond:
        countPerSecond = 1
        lastSecond = currentSecond
        if not abs(currentMinute - lastMinute)<= 2:
            countPer2Minutes = 1
            lastMinute = currentMinute
    return response
