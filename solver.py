""" Instances of this class can be used to determine the best move given
    the current game state.
"""
import numpy as np
from sys import stdout
from random import shuffle

from states import ShipState


LIMIT = 2**20

default_score = np.array([
    [10, 15, 19, 21, 22, 22, 21, 19, 15, 10],
    [15, 20, 24, 26, 27, 27, 26, 24, 20, 15],
    [19, 24, 28, 30, 31, 31, 30, 28, 24, 19],
    [21, 26, 30, 32, 33, 33, 32, 30, 26, 21],
    [22, 27, 31, 33, 34, 34, 33, 31, 27, 22],
    [22, 27, 31, 33, 34, 34, 33, 31, 27, 22],
    [21, 26, 30, 32, 33, 33, 32, 30, 26, 21],
    [19, 24, 28, 30, 31, 31, 30, 28, 24, 19],
    [15, 20, 24, 26, 27, 27, 26, 24, 20, 15],
    [10, 15, 19, 21, 22, 22, 21, 19, 15, 10]
]) ** 2 * 16


length5_configs = [
    (x, y, v) for x in range(10)
    for y in range(10)
    for v in [True, False]
    if ((y + 4 < 10) if v else (x + 4 < 10))
]

length4_configs = [
    (x, y, v) for x in range(10)
    for y in range(10)
    for v in [True, False]
    if ((y + 3 < 10) if v else (x + 3 < 10))
]

length3_configs = [
    (x, y, v) for x in range(10)
    for y in range(10)
    for v in [True, False]
    if ((y + 2 < 10) if v else (x + 2 < 10))
]

length2_configs = [
    (x, y, v) for x in range(10)
    for y in range(10)
    for v in [True, False]
    if ((y + 1 < 10) if v else (x + 1 < 10))
]


def board_config_generator(board, ships):
    configs = [length2_configs, length3_configs, length3_configs,
               length4_configs, length5_configs]
    for index in range(5):
        ship = ships[index]
        if ship.isSunk:
            configs[index].clear()
            configs[index].append(ship.x, ship.y, ship.isVertical)
        else:
            front = []
            back = []
            for (x, y, v) in configs[index]:
                occupied = set([(x+(0 if v else i), y+(i if v else 0))
                                for i in range(ship.length)])
                valid = True
                hit = False
                for _x, _y in occupied:
                    if board[_x, _y] < 0:
                        valid = False
                    elif board[_x, _y] > 0:
                        hit = True
                if valid:
                    if hit:
                        front.append((x, y, v))
                    else:
                        back.append((x, y, v))
            shuffle(front), shuffle(back)
            configs[index] = front + back
    len2, len3a, len3b, len4, len5 = configs
    count = 0
    for (xA, yA, vA) in len2:
        if count > LIMIT:
            break
        shipA = ShipState(xA, yA, 2, vA)
        for (xB, yB, vB) in len3a:
            if count > LIMIT:
                break
            shipB = ShipState(xB, yB, 3, vB)
            if len(shipB.cells & shipA.cells) > 0:
                continue
            for (xC, yC, vC) in len3b:
                if count > LIMIT:
                    break
                shipC = ShipState(xC, yC, 3, vC)
                if len(shipC.cells & (shipA.cells | shipB.cells)) > 0:
                    continue
                for (xD, yD, vD) in len4:
                    if count > LIMIT:
                        break
                    shipD = ShipState(xD, yD, 4, vD)
                    if len(shipD.cells & (shipA.cells | shipB.cells
                           | shipC.cells)) > 0:
                        continue
                    for (xE, yE, vE) in len5:
                        shipE = ShipState(xE, yE, 5, vE)
                        if len(shipE.cells & (shipA.cells | shipB.cells
                               | shipC.cells | shipD.cells)) > 0:
                            continue
                        exact = np.ones((10, 10)) * -1
                        for ship in [shipA, shipB, shipC, shipD, shipE]:
                            for cell in ship.cells:
                                exact[cell] = ship.length
                        count += 1
                        if count % 32768 == 0:
                            stdout.write("\r||=="+str(count).rjust(11, "=")+"========||")
                        yield exact
    stdout.write("\r||=="+str(count).rjust(11, "=")+"========||\n")


def score_cells(board, ships):
    cells = np.zeros((10, 10))
    board_gen = board_config_generator(board, ships)
    done = False
    for test in board_gen:
        if test is None:
            break
        if not done:
            print(test, "\n", board)
            done = True
        if np.any((test * board) < 0):
            continue
        test[test > 2] = 1
        test[test < 3] = 0
        cells += test
    if np.sum(cells) >= LIMIT * 15:
        cells += default_score
    for x in range(10):
        for y in range(10):
            if board[x, y] != 0:
                cells[x, y] = 0
    max_score = np.max(cells)
    best_cell = [(x, y) for x in range(10) for y in range(10) if cells[x, y] >= max_score * 0.9]
    return int(np.sum(cells)), best_cell  # TODO: CHANGE LATER
