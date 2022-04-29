import os
import sys

sys.path.append('/home/rgarcia/projects/lolstats')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolstats.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from summoners.models import Summoner
from summoners.models import Game
from summoners.models import GameRecord

def main():
    """."""
    games = Game.objects.all()
    limit = 10
    i = 0
    for g in games:
        if i >= limit:
            break
        print(get_participants(g))
        i += 1

def get_participants(game):
    """."""
    return GameRecord.objects.filter(game__id=game.id)
        

if __name__ == "__main__":
    main()
