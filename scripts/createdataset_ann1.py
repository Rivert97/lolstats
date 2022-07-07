import os
import sys
import numpy as np

sys.path.append('/home/rgarcia/projects/lolstats')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolstats.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from summoners.models import Summoner
from summoners.models import Game
from summoners.models import GameRecord
from summoners.models import SummonerChampionStats
from summoners.models import SummonerStats

MAX_LEVEL = 1200
MAX_MATCHES = 40
MAX_CHAMPION_POINTS = 6000000 #6,000,000
MAX_KDA = 100

def main():
    """."""
    summoners = Summoner.objects.all()
    start = 0
    i = start
    # Iteramos sobre cada invocador
    for summoner in summoners[start:]:
        games_dataset = GameRecord.objects.filter(summoner=summoner).order_by('-game__gamedate')[:10]
        # Iteramos cada juego para el dataset
        summoner_records = []
        game_results = []
        j = 0
        for game in games_dataset:
            game_row = []
            # Obtenemos los 5 invocadores del equipo 1
            records1 = GameRecord.objects.filter(game__id=game.game.id, teamid=100)
            for record in records1:
                history = GameRecord.objects.filter(summoner=record.summoner).order_by('-game__gamedate')[j+1:41+j]
                player_row = process_player_history(history, game)
                game_row = game_row + player_row
            # Obtenemos los 5 invocadores del equipo 2
            records2 = GameRecord.objects.filter(game__id=game.game.id, teamid=200)
            for record in records2:
                history = GameRecord.objects.filter(summoner=record.summoner).order_by('-game__gamedate')[j+1:41+j]
                player_row = process_player_history(history, game)
                game_row = game_row + player_row
            if len(game_row) != 80:
                print("Omitiendo partida por falta de datos:", game)
            else:
                summoner_records.append(game_row)
                # Guardamos el equipo ganador del juego
                if records1[0].win:
                    game_results.append(0)
                else:
                    game_results.append(1)
            print("Game:", j, "->", game)
            j += 1
        filepath = "/datos/lolstats/datasets_ann1/%s.csv" %(summoner.id)
        filepath_truth = "/datos/lolstats/datasets_ann1/%s_truth.csv" %(summoner.id)
        dataset = np.array(summoner_records)
        dataset_truth = np.array(game_results)
        np.savetxt(filepath, dataset, delimiter=',')
        np.savetxt(filepath_truth, dataset_truth, delimiter=',')
        print("Summoner:", i, "->", summoner)
        i += 1

def process_player_history(history, record):
    """."""
    n_matches = 0
    kda_sum = 0
    wins = 0
    win_streak = 0
    champion_wins = 0
    champion_games = 0
    champion_kda_sum = 0
    for match in history:
        if match.win:
            wins += 1
            win_streak += 1
        else:
            win_streak = 0
        if match.champion == record.champion:
            champion_games += 1
            champion_kda_sum += match.kda
            if match.win:
                champion_wins += 1
        kda_sum += match.kda
        n_matches += 1
    # Obtenemos la maestria del campeon
    try:
        summchamp = SummonerChampionStats.objects.get(summoner=record.summoner, champion=record.champion)
        championpoints = summchamp.championpoints
    except SummonerChampionStats.DoesNotExist:
        championpoints = 0
    # Obtenemos las estadisticas del invocador
    summstats = SummonerStats.objects.get(summoner=record.summoner)
    if champion_games == 0:
        champion_winrate = 0
        champion_meankda = 0
    else:
        champion_winrate = champion_wins/champion_games
        champion_meankda = (champion_kda_sum/champion_games)/MAX_KDA
    if n_matches == 0:
        winrate = 0
        meankda = 0
    else:
        winrate = wins/n_matches
        meankda = kda_sum/n_matches
    player_row = [
            summstats.level/MAX_LEVEL,
            winrate,
            (win_streak)/MAX_MATCHES,
            meankda/MAX_KDA,
            championpoints/MAX_CHAMPION_POINTS,
            champion_winrate,
            champion_meankda,
            champion_games/MAX_MATCHES
        ]
    return player_row

def process_game_record(record):
    """."""
    # Para cada participante obtenemos su historial y estadisticas
    history = GameRecord.objects.filter(summoner=record.summoner)[:MAX_MATCHES]
    n_matches = 0
    kda_sum = 0
    wins = 0
    win_streak = 0
    champion_wins = 0
    champion_games = 0
    champion_kda_sum = 0
    for match in history:
        if match.win:
            wins += 1
            win_streak += 1
        else:
            win_streak = 0
        if match.champion == record.champion:
            champion_games += 1
            champion_kda_sum += match.kda
            if match.win:
                champion_wins += 1
        kda_sum += match.kda
        n_matches += 1
    # Obtenemos la maestria del campeon
    try:
        summchamp = SummonerChampionStats.objects.get(summoner=record.summoner, champion=record.champion)
        championpoints = summchamp.championpoints
    except SummonerChampionStats.DoesNotExist:
        championpoints = 0
    # Obtenemos las estadisticas del invocador
    summstats = SummonerStats.objects.get(summoner=record.summoner)
    if champion_games == 0:
        champion_winrate = 0
        champion_meankda = 0
    else:
        champion_winrate = champion_wins/champion_games
        champion_meankda = (champion_kda_sum/champion_games)/MAX_KDA
    player_row = [
            summstats.level/MAX_LEVEL,
            wins/n_matches,
            (win_streak)/MAX_MATCHES,
            (kda_sum/n_matches)/MAX_KDA,
            championpoints/MAX_CHAMPION_POINTS,
            champion_winrate,
            champion_meankda,
            champion_games/MAX_MATCHES
        ]
    return player_row


if __name__ == "__main__":
    main()
