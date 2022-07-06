import os
import sys
import json
from datetime import datetime

sys.path.append('/home/rgarcia/projects/lolstats')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolstats.settings")

from django.core.wsgi import get_wsgi_application
from django.utils import timezone
application = get_wsgi_application()
from summoners.models import Summoner
from summoners.models import SummonerStats
from summoners.models import Game
from summoners.models import GameRecord
from champions.models import Champion

def fill_all():
    """."""
    tz = timezone.get_current_timezone()
    games = Game.objects.all()
    start = 141664
    i = start
    for game in games[start:]:
        data = game.fetch_file()
        if 'info' not in data:
            print("Omitiendo partida", game, "archivo corrupto")
            continue
        ts = int(data['info']['gameCreation']) / 1000
        gamedate = datetime.utcfromtimestamp(ts)
        timezone_datetime = timezone.make_aware(gamedate, tz, True)
        game.gamedate = timezone_datetime
        game.save()
        for player in data['info']['participants']:
            try:
                summ = Summoner.objects.get(puuid=player['puuid'])
            except Summoner.DoesNotExist:
                print("Omitiendo invocador", player['puuid'])
                continue
            try:
                record = GameRecord.objects.get(game=game, summoner=summ)
            except GameRecord.DoesNotExist:
                record = GameRecord(game=game, summoner=summ)
            record.teamid = player['teamId']
            try:
                champion = Champion.objects.get(championid=player['championId'])
            except Champion.DoesNotExist:
                print("Omitiendo campeon", player['championId'])
                continue
            record.champion = champion
            record.win = player['win']
            if player['deaths'] == 0:
                kda = player['kills'] + player['assists']
            else:
                kda = (player['kills'] + player['assists']) / player['deaths']
            record.kda = kda
            record.save()
            print(i, "->", summ)
        i += 1

def fill_kda():
    """."""
    games = Game.objects.all()
    start = 155102
    i = start
    for game in games[start:]:
        data = game.fetch_file()
        if 'info' not in data:
            print("Omitiendo partida", game, "archivo corrupto")
            continue
        for player in data['info']['participants']:
            try:
                summ = Summoner.objects.get(puuid=player['puuid'])
            except Summoner.DoesNotExist:
                print("Omitiendo invocador", player['puuid'])
                continue
            try:
                record = GameRecord.objects.get(game=game, summoner=summ)
            except GameRecord.DoesNotExist:
                print("Omitiendo record", record)
                continue
            if player['deaths'] == 0:
                kda = player['kills'] + player['assists']
            else:
                kda = (player['kills'] + player['assists']) / player['deaths']
            record.kda = kda
            record.save()
            print(i, "->", summ)
        i += 1


def main():
    #fill_all()
    fill_kda()

if __name__ == '__main__':
    main()
