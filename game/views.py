from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Game, GameMove
from .serializers import GameMoveSerializer, GameSerializer
import random
import string
import logging

logger = logging.getLogger(__name__)

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    @action(detail=False, methods=['post'])
    def create_game(self, request):
        try:
            # Generate unique room code
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            while Game.objects.filter(room_code=room_code).exists():
                room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Create new game
            game = Game.objects.create(
                room_code=room_code,
                player1=request.user,
                status='PENDING',
                board='---------'
            )
            
            return Response({
                'status': 'success',
                'message': 'Game created successfully',
                'data': {
                    'room_code': room_code,
                    'player1': request.user.username,
                    'status': 'PENDING',
                    'websocket_url': f'ws://127.0.0.1:8000/ws/game/{room_code}/'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Game Creation Error: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to create game',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def join_game(self, request):
        try:
            room_code = request.data.get('room_code')
            if not room_code:
                return Response({
                    'status': 'error',
                    'message': 'Room code is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            game = Game.objects.filter(room_code=room_code).first()
            if not game:
                return Response({
                    'status': 'error',
                    'message': 'Game not found'
                }, status=status.HTTP_404_NOT_FOUND)

            if game.status != 'PENDING':
                return Response({
                    'status': 'error',
                    'message': 'Game is already in progress or completed'
                }, status=status.HTTP_400_BAD_REQUEST)

            if game.player1 == request.user:
                return Response({
                    'status': 'error',
                    'message': 'You cannot join your own game'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'status': 'success',
                'message': 'Game found',
                'data': {
                    'room_code': room_code,
                    'player1': game.player1.username,
                    'status': game.status,
                    'websocket_url': f'ws://127.0.0.1:8000/ws/game/{room_code}/'
                }
            })

        except Exception as e:
            logger.error(f"Join Game Error: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to join game',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=False, methods=['get'])
    def game_history(self, request):
        try:
            games = Game.objects.filter(player1=request.user) | Game.objects.filter(player2=request.user)
            data = []
            for game in games:
                moves = GameMove.objects.filter(game=game)
                data.append({
                    'room_code': game.room_code,
                    'player1': game.player1.email,
                    'player2': game.player2.email if game.player2 else None,
                    'status': game.status,
                    'winner': game.winner.email if game.winner else None,
                    'moves': GameMoveSerializer(moves, many=True).data
                })
            
            return Response({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            logger.error(f"Game History Error: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to get game history',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        

    
        

    
