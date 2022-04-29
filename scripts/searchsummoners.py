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

QUEUE = "RANKED_SOLO_5x5"
TIERS = ["MASTER"]
DIVISIONS = ["I", "II", "III", "IV"]
PAGES = ["1", "2", "3", "4", "5"] 

def process_summoner(sid):
    """."""
    try:
        summoner = Summoner.objects.get(summonerid=sid)
    except Summoner.DoesNotExist:
        summoner = Summoner(summonerid=sid)
        status = summoner.search_summoner()
        if 200 == status:
            summoner.save()
            summoner.save_json()
        else:
            print("No se pudo obtener los datos del invocador %s" %(sid))
            sys.exit(1)
    print(summoner)

    gameids = summoner.search_games(count=100)
    gamecount = 1
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
        print('\t', gamecount, ':', game, end='\r')
        if gamedata != None:
            teamid = 0
            for participant in gamedata['info']['participants']:
                if participant['puuid'] == summoner.puuid:
                    teamid = int(participant['teamId'])
            try:
                record = GameRecord.objects.get(summoner_id=summoner.id, game_id=game.id)
            except GameRecord.DoesNotExist:
                record = GameRecord(summoner_id=summoner.id, game_id=game.id, teamid=teamid)
                record.save()
            print('\t\t', record, end='\r')
        gamecount += 1
    print("")

def main():
    for tier in TIERS:
        for division in DIVISIONS:
            for page in PAGES:
                print("Tier:", tier, ", Division:", division, ", Page:", page)
                tierlist = Summoner.search_summoner_list(QUEUE, tier, division, page)
                if 0 == len(tierlist):
                    print("No se encontro la lista de invocadores para %s %s pagina %s" %(tier, division, page))
                    break
                summonerids = [t['summonerId'] for t in tierlist]

                summonercount = 1
                for sid in summonerids:
                    print(summonercount, ":", end='')
                    process_summoner(sid)
                    summonercount += 1

if __name__ == '__main__':
    main()

