# game/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from authenticate.models import User
from .models import Game, GameMove
from django.core.exceptions import ObjectDoesNotExist
import jwt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TicTacToeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'game_{self.room_code}'
        
        # Get token from query string
        query_string = self.scope['query_string'].decode()
        token = dict(pair.split('=') for pair in query_string.split('&')).get('token', '')
        
        try:
            # Verify JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            self.user_id = payload['user_id']
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Add player to game and notify
            game_state = await self.add_player_to_game()
            if game_state:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    game_state
                )
            
            # Send initial game state
            initial_state = await self.get_game_state()
            if initial_state:
                await self.send(text_data=json.dumps(initial_state))
            
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT Token Error: {str(e)}")
            await self.close()
        except Exception as e:
            logger.error(f"Connection Error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Disconnect Error: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'make_move':
                position = data.get('position')
                game_state = await self.make_move(position)
                if game_state:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        game_state
                    )
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Receive Error: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    @database_sync_to_async
    def get_game_state(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            return {
                'action': 'game_state',
                'board': game.board,
                'status': game.status,
                'current_turn': game.current_turn.username if game.current_turn else None,
                'player1': game.player1.username,
                'player2': game.player2.username if game.player2 else None,
                'winner': game.winner.username if game.winner else None
            }
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def add_player_to_game(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            user = User.objects.get(id=self.user_id)
            
            if game.player2 is None and game.player1 != user:
                game.player2 = user
                game.status = 'IN_PROGRESS'
                game.current_turn = game.player1
                game.save()
                
                return {
                    'type': 'game_message',
                    'message': {
                        'action': 'player_joined',
                        'player2': user.username,
                        'status': 'IN_PROGRESS',
                        'current_turn': game.player1.username,
                        'board': game.board
                    }
                }
            return None
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Add Player Error: {str(e)}")
            return None
    
    @database_sync_to_async
    def make_move(self, position):
        try:
            game = Game.objects.get(room_code=self.room_code)
            user = User.objects.get(id=self.user_id)
            
            if (game.status != 'IN_PROGRESS' or 
                game.current_turn != user or 
                not (0 <= position <= 8) or 
                game.board[position] != '-'):
                return None
            
            # Update board
            board_list = list(game.board)
            symbol = 'X' if user == game.player1 else 'O'
            board_list[position] = symbol
            game.board = ''.join(board_list)
            
            # Save move
            GameMove.objects.create(
                game=game,
                player=user,
                position=position
            )
            
            # Check for winner
            winning_combinations = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
                [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
                [0, 4, 8], [2, 4, 6]  # Diagonals
            ]
            
            for combo in winning_combinations:
                if all(board_list[i] == symbol for i in combo):
                    game.status = 'COMPLETED'
                    game.winner = user
                    game.save()
                    return {
                        'type': 'game_message',
                        'message': {
                            'action': 'game_over',
                            'winner': user.username,
                            'board': game.board,
                            'winning_combo': combo
                        }
                    }
            
            # Check for draw
            if '-' not in game.board:
                game.status = 'COMPLETED'
                game.save()
                return {
                    'type': 'game_message',
                    'message': {
                        'action': 'game_over',
                        'winner': None,
                        'board': game.board,
                        'status': 'draw'
                    }
                }
            
            # Switch turns
            game.current_turn = game.player2 if user == game.player1 else game.player1
            game.save()
            
            return {
                'type': 'game_message',
                'message': {
                    'action': 'move_made',
                    'position': position,
                    'symbol': symbol,
                    'next_turn': game.current_turn.username,
                    'board': game.board
                }
            }
            
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Make Move Error: {str(e)}")
            return None

    async def game_message(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps(message))
        except Exception as e:
            logger.error(f"Game Message Error: {str(e)}")