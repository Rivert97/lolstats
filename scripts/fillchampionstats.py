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
from summoners.models import SummonerChampionStats
from champions.models import Champion

def main():
    summoners = Summoner.objects.all()
    start = 0
    i = start
    for summ in summoners[start:]:
        champions = summ.search_champions_mastery()
        for champ in champions:
            try:
                dbchamp = Champion.objects.get(championid=champ['championId'])
            except Champion.DoesNotExist:
                print("Campeon %s no encontrado" %(champ['championId'],))
                sys.exit(1)
            try:
                stats = SummonerChampionStats.objects.get(summoner=summ, champion=dbchamp)
            except SummonerChampionStats.DoesNotExist:
                stats = SummonerChampionStats(summoner=summ, champion=dbchamp)
            stats.championpoints = champ['championPoints']
            stats.save()
            print(i, "->", stats)
        i += 1

if __name__ == "__main__":
    main()
