"""
Launch file for the Battleship application.


"""

import numpy as np

from solver import *
from states import ShipState, GameState


if __name__ == "__main__":
    shipsA = [
        ShipState(0, 5, 2, True),
        ShipState(1, 0, 3, True),
        ShipState(9, 5, 3, True),
        ShipState(3, 4, 4),
        ShipState(4, 0, 5)
    ]
    shipsB = [
        ShipState(5, 5, 2, True),
        ShipState(1, 0, 3),
        ShipState(1, 7, 3),
        ShipState(2, 2, 4, True),
        ShipState(4, 9, 5)
    ]
    scoreA, scoreB = 30093975536, 30093975536
    bestA, bestB = ["E5", "E6", "F5", "F6"], ["E5", "E6", "F5", "F6"]
    game = GameState(shipsA, shipsB)
    game.show(True)
    while any([not x.isSunk for x in game.shipsA]) and any([not x.isSunk for x in game.shipsB]):
        board = game.boardA if game.playerA else game.boardB
        prompt = "Player" + ("A" if game.playerA else "B")
        cell = input(prompt + " -- Enter a cell coordinate: ")
        valid = False
        while not valid:
            if cell == "exit":
                exit(0)
            if not ("A" <= cell[0] <= "J" and 1 <= int(cell[1:]) <= 10):
                cell = input("Invalid cell. Enter another: ")
            elif board[GameState.index(cell)] != 0:
                cell = input("This cell has already been hit. Enter another: ")
            else:
                valid = True
        playerTurn = game.playerA
        game.play(cell)
        game.show(True)
        if playerTurn:
            scoreA, bestA = score_cells(game.boardA, game.shipsB)
            bestA = [convert(a) for a in bestA]
        else:
            scoreB, bestB = score_cells(game.boardB, game.shipsA)
            bestB = [convert(b) for b in bestB]
        print("     "+str(scoreA).center(11)+"        |        "+str(scoreB).center(11)+"      ")
        print("BEST CELLS: " + str(bestA if playerTurn else bestB))
    print()
    if all([x.isSunk for x in shipsB]):
        print("Player A is the winner!")
    else:
        print("Player B is the winner!")
