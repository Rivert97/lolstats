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
    """."""
    startindex = 3351
    summonercount = startindex + 1
    summoners = Summoner.objects.all()
    for summoner in summoners[startindex:]:
        gameids = summoner.search_games(count=50)
        gamecount = 1
        print(summonercount, ':', summoner)
        for gid in gameids:
            try:
                game = Game.objects.get(gameid=gid)
                gamedata = None
            except Game.DoesNotExist:
                game = Game(gameid=gid)
                game.save()
                if game.search_details():
                    game.save_json()
                    gamedata = json.loads(game.jsondata)
                else:
                    print("No se pudo obtener los detalles de la partida %s" %(gid))
                    sys.exit(1)
            print(" " * 50, end='\r')
            print('\t', gamecount, ':', game, end='\r')
            if gamedata != None:
                teamid = 0
                for participant in gamedata['info']['participants']:
                    if participant['puuid'] == summoner.puuid:
                        teamid = int(participant['teamId'])
                        break
                try:
                    record = GameRecord.objects.get(summoner_id=summoner.id, game_id=game.id)
                except GameRecord.DoesNotExist:
                    record = GameRecord(summoner_id=summoner.id, game_id=game.id, teamid=teamid)
                    record.save()
                print('\t\t', record, end='\r')
            gamecount += 1
        summonercount += 1
        print("")

if __name__ == "__main__":
    main()
