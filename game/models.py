from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Game(models.Model):
    GAME_STATUS = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )
    
    room_code = models.CharField(max_length=8, unique=True)
    player1 = models.ForeignKey(User, related_name='games_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='games_as_player2', on_delete=models.CASCADE, null=True)
    current_turn = models.ForeignKey(User, related_name='games_as_current_turn', on_delete=models.CASCADE, null=True)
    winner = models.ForeignKey(User, related_name='games_won', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, choices=GAME_STATUS, default='PENDING')
    board = models.CharField(max_length=9, default='---------')  # - for empty, X for player1, O for player2
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.room_code} - {self.status}"

class GameMove(models.Model):
    game = models.ForeignKey(Game, related_name='moves', on_delete=models.CASCADE)
    player = models.ForeignKey(User, related_name='moves', on_delete=models.CASCADE)
    position = models.IntegerField()  # 0-8 for board positions
    created_at = models.DateTimeField(auto_now_add=True)
