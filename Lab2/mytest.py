from player import Player
from factory import PlayerFactory
import json
player = Player("Alpha", "alpha@gmail.com", "2000-04-04", 455, "Berserk")
player2 = Player("Alpha", "alpha@gmail.com", "2000-04-04", 455, "Berserk")
factory = PlayerFactory()

players = [
            Player("Alpha", "alpha@gmail.com", "2000-04-04", 455, "Berserk"),
            Player("Beta", "beta@gmail.com", "2001-06-10", 657, "Tank")
        ]
factory.from_json(players)
