""" Instances of this class can be used to determine the best move given
    the current game state.
"""
import pickle
import numpy as np
from sys import stdout
import random

from tqdm import tqdm

from states import ShipState


LIMIT = 2**12

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
], dtype=np.float64)
default_score /= np.sum(default_score)

board_list = pickle.load(open("board/sample_65642.dat", "rb"))["list"]


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


def convert(coord):
    letter = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    result = letter[coord[0]] + str(coord[1]+1)
    if len(coord) == 2:
        return result
    return result + "-V" if coord[3] else "-H"


def board_config_generator(board, ships, shuffle=False):
    configs = [length2_configs, length3_configs, length3_configs,
               length4_configs, length5_configs]
    for index in range(5):
        ship = ships[index]
        if ship.isSunk:
            configs[index].clear()
            configs[index].append((ship.x, ship.y, ship.isVertical))
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
            if shuffle:
                random.shuffle(front)
                random.shuffle(back)
            configs[index] = front + back
    len2, len3a, len3b, len4, len5 = configs
    estimate = len(len2) * len(len3a) * len(len3b) * len(len4) * len(len5)
    if estimate > 2 ** 18:
        for board, ships in board_list:
            yield board, None
        return
    count = 0
    for (xA, yA, vA) in len2:
        if count > LIMIT:
            break
        shipA = ShipState(xA, yA, vA, 2)
        for (xB, yB, vB) in len3a:
            if count > LIMIT:
                break
            shipB = ShipState(xB, yB, vB, 3)
            if len(shipB.cells & shipA.cells) > 0:
                continue
            for (xC, yC, vC) in len3b:
                if count > LIMIT:
                    break
                shipC = ShipState(xC, yC, vC, 3)
                if len(shipC.cells & (shipA.cells | shipB.cells)) > 0:
                    continue
                for (xD, yD, vD) in len4:
                    if count > LIMIT:
                        break
                    shipD = ShipState(xD, yD, vD, 4)
                    if len(shipD.cells & (shipA.cells | shipB.cells
                           | shipC.cells)) > 0:
                        continue
                    for (xE, yE, vE) in len5:
                        shipE = ShipState(xE, yE, vE, 5)
                        if len(shipE.cells & (shipA.cells | shipB.cells
                               | shipC.cells | shipD.cells)) > 0:
                            continue
                        exact = np.ones((10, 10), dtype=np.int8) * -1
                        ships = [shipA, shipB, shipC, shipD, shipE]
                        for ship in ships:
                            for cell in ship.cells:
                                exact[cell] = ship.length
                        count += 1
                        yield exact, ships


def generate_random_board():
    board = np.ones((10, 10), dtype=np.int8) * -1
    shipA, shipB, shipC, shipD, shipE = None, None, None, None, None
    while True:
        shipA = ShipState(*(random.choice(length2_configs)), length=2)
        shipB = ShipState(*(random.choice(length3_configs)), length=3)
        shipC = ShipState(*(random.choice(length3_configs)), length=3)
        shipD = ShipState(*(random.choice(length4_configs)), length=4)
        shipE = ShipState(*(random.choice(length5_configs)), length=5)
        test_board = np.zeros((10, 10), dtype=np.int8)
        for ship in [shipA, shipB, shipC, shipD, shipE]:
            for cell in ship.cells:
                test_board[cell] = 1
                board[cell] = ship.length
        if np.sum(test_board) != 17:
            board = np.ones((10, 10), dtype=np.int8) * -1
            continue
        break
    return board, [shipA, shipB, shipC, shipD, shipE]


def score_cells(board):
    cells = np.zeros((10, 10))
    done = False
    for test, ships in board_list:
        if test is None:
            break
        if not done:
            print(test, "\n", board)
            done = True
        if np.any((test * board) < 0):
            continue
        reduced = test + 1
        reduced[reduced > 0] = 1
        cells += reduced
    for x in range(10):
        for y in range(10):
            if board[x, y] != 0:
                cells[x, y] = 0
    max_score = np.max(cells)
    best_cell = [(x, y) for x in range(10) for y in range(10) if cells[x, y] == max_score]
    return int(np.sum(cells)), best_cell  # TODO: CHANGE LATER


def create_random_samples():
    sample = {
        "total": np.zeros((10, 10), dtype=np.int32),
        "list": []
    }
    minimum = 2 ** 16.5
    max_skips = 2 ** 18
    skips = 0
    progress = tqdm(ncols=60, total=max_skips, position=0, ascii='_...:::!!!|', postfix={"TOTAL": len(sample["list"])}, leave=True)
    while skips < max_skips:
        options = []
        for _ in range(8):
            options.append(generate_random_board())
        result = [(0, None) for _ in options]
        for index in range(len(options)):
            option, ships = options[index]
            reduced = option[:, :]
            reduced[reduced > 0] = 1
            reduced[reduced < 0] = 0
            combo = reduced + sample["total"]
            diff = np.sum((default_score - (combo / np.sum(combo)))**2)
            result[index] = (diff, option, ships)
        result.sort(key=lambda x: x[0])
        selected = result[0]
        if len(sample["list"]) > minimum:
            if selected[0] > np.sum((default_score - (sample["total"].astype(np.float64) / np.sum(sample["total"])))**2):
                skips += 1
                progress.update(1)
                continue
        skips = 0
        progress.reset()
        progress.set_postfix({"TOTAL": len(sample["list"])})
        sample["list"].append((selected[1], selected[2]))
        sample["total"] += selected[1]
    progress.close()
    print(sample["total"])
    print(len(sample["list"]))
    print()
    pickle.dump(sample, open("board/sample_"+str(len(sample["list"]))+".dat", "wb"))

