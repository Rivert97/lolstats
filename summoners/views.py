from django.shortcuts import render
import json
from .models import Summoner
from .models import Game
from .models import GameRecord

REGIONS = ['NA', 'LAN', 'LAS']

def index(request, region=""):
    """Muestra la pantalla principal de seccion summoners."""
    if region.upper() not in REGIONS:
        region = 'LAN'
    context = {
            'region': region.upper(),
            'regions': REGIONS,
            }
    return render(request, 'summoners/index.html', context)

def detail(request, region, summoner_name):
    """Busca y muestra la información de un invocador."""
    if region.upper() not in REGIONS:
        region = 'LAN'
    try:
        summoner = Summoner.objects.get(name=summoner_name)
    except Summoner.DoesNotExist:
        summoner = Summoner(name=summoner_name)
        summoner.search_summoner(region)
        summoner.save()
        summoner.save_json()
    gamesids = summoner.search_games(count=1)
    games = []
    records = []
    for gid in gamesids:
        try:
            game = Game.objects.get(gameid=gid)
        except Game.DoesNotExist:
            game = Game(gameid=gid)
            game.save()
        game.search_details()
        game.save_json()
        games.append(game)
        gamedata = json.loads(game.jsondata)
        teamid = 0
        for participant in gamedata['info']['participants']:
            if participant['puuid'] == summoner.puuid:
                teamid = int(participant['teamId'])
                break
        try:
            record = GameRecord.objects.get(summoner_id=summoner.id, game_id=game.id)
        except:
            record = GameRecord(summoner_id=summoner.id, game_id=game.id, teamid=teamid)
            record.save()
        records.append(record)
    context = {
            'summonerName': summoner_name,
            'summoner': summoner,
            'games': games,
            'records': records,
            }

    return render(request, 'summoners/detail.html', context)
