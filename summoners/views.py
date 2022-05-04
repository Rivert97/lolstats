from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Summoner
from .models import Game
from .models import GameRecord
from .serializers import SummonerSerializer
from .serializers import GameSerializer

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

@csrf_exempt
def summoner_api(request, summonerid=""):
    if request.method == "GET":
        if summonerid != "":
            summoner = Summoner.objects.get(summonerid=summonerid)
            summoners_serializer = SummonerSerializer(summoner)
        else:
            summoners = Summoner.objects.all()
            summoners_serializer = SummonerSerializer(summoners, many=True)
        return JsonResponse(summoners_serializer.data, safe=False)
    elif request.method == "POST":
        summoner_data = JSONParser().parse(request)
        summoners_serializer = SummonerSerializer(data=summoner_data)
        if summoners_serializer.is_valid():
            summoners_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == "PUT":
        summoner_data = JSONParser().parse(request)
        summoner = Summoner.objects.get(summonerid=summoner_data['summonerid'])
        summoners_serializer = SummonerSerializer(summoner, data=summoner_data)
        if summoners_serializer.is_valid():
            summoners_serializer.save()
            return JsonResponse("Update Successfully", safe=False)
        return JsonResponse("Failed to Update")
    elif request.method == "DELETE":
        summoner = Summoner.objects.get(summonerid=summonerid)
        summoner.delete()
        return JsonResponse("Deleted Successfully", safe=False)

@csrf_exempt
def game_api(request, gameid=""):
    if request.method == "GET":
        if gameid != "":
            game = Game.objects.get(gameid=gameid)
            games_serializer = GameSerializer(game)
        else:
            games = Game.objects.all()
            games_serializer = GameSerializer(games, many=True)
        return JsonResponse(games_serializer.data, safe=False)
    elif request.method == "POST":
        game_data = JSONParser().parse(request)
        games_serializer = GameSerializer(data=game_data)
        if games_serializer.is_valid():
            games_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == "PUT":
        game_data = JSONParser().parse(request)
        game = Game.objects.get(gameid=game_data['gameid'])
        games_serializer = GameSerializer(game, data=game_data)
        if games_serializer.is_valid():
            games_serializer.save()
            return JsonResponse("Update Successfully", safe=False)
        return JsonResponse("Failed to Update")
    elif request.method == "DELETE":
        game = Game.objects.get(gameid=gameid)
        game.delete()
        return JsonResponse("Deleted Successfully", safe=False)
