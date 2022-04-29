import os
import sys
import json

sys.path.append('/home/rgarcia/projects/lolstats')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolstats.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from summoners.models import Summoner
from summoners.models import Game
from summoners.models import GameRecord

def main():
    #startindex = 29322
    startindex = 30146
    games = Game.objects.all()
    gamecount = startindex + 1
    summonercount = 1
    for game in games[startindex:]:
        fetch_result = game.fetch_info()
        if not fetch_result:
            print("No se encontro el archivo para partida: %s" %(game))
            continue
        participants = game.fetch_participants()
        for participant in participants:
            try:
                summoner = Summoner.objects.get(puuid=participant['puuid'])
            except Summoner.DoesNotExist:
                summoner = Summoner(puuid=participant['puuid'])
                status = summoner.search_summoner()
                if 200 == status:
                    summoner.save()
                    summoner.save_json()
                elif 404 == status:
                    print("No se pudo obtener los datos del invocador %s" %(participant['puuid']))
                    continue
                else:
                    print("No se pudo obtener los datos del invocador %s" %(participant['puuid']))
                    sys.exit(1)

            # Guardamos el registro del equipo
            try:
                record = GameRecord.objects.get(summoner_id=summoner.id, game_id=game.id)
                #print("Registro de juego ya guardado")
            except GameRecord.DoesNotExist:
                #print("Guardando registro de juego...")
                record = GameRecord(summoner_id=summoner.id, game_id=game.id, teamid=participant['teamId'])
                record.save()
            print(gamecount, ':', summonercount, '->', participant['puuid'])
            summonercount += 1
        gamecount += 1
        #break

def main_old():
    summoners = Summoner.objects.all()
    for summoner in summoners:
        record = GameRecord.objects.select_related().filter(summoner = summoner.id)
        for r in record:
            r.game.fetch_info()
            print(r.game.fetch_participants())
        break


if __name__ == '__main__':
    main()
