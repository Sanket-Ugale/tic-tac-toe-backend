from rest_framework import serializers
from .models import Game, GameMove

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class GameMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMove
        fields = '__all__'