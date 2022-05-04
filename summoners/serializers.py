from rest_framework import serializers
from .models import Summoner
from .models import Game

class SummonerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summoner
        fields = ('summonerid', 'puuid', 'level', 'region')

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('gameid',)