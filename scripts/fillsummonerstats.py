import os
import sys
import json

sys.path.append('/home/rgarcia/projects/lolstats')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolstats.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from summoners.models import Summoner
from summoners.models import SummonerStats
from summoners.models import Game
from summoners.models import GameRecord

def main():
    summoners = Summoner.objects.all()
    i = 0
    for summ in summoners:
        data = summ.fetch_file()
        try:
            stats = SummonerStats.objects.get(summoner=summ)
        except SummonerStats.DoesNotExist:
            stats = SummonerStats(summoner=summ)
        stats.level = data['summonerLevel']
        rank = summ.fetch_rank()
        if rank is None:
            print("Omitiendo invocador", summ)
            continue
        stats.tier = rank['tier']
        stats.division = rank['division']
        stats.winrate = 0
        stats.winstreak = 0
        stats.meankda = 0
        stats.save()
        print(i, "->", summ)
        i += 1

if __name__ == '__main__':
    main()
