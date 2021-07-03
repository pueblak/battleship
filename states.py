import numpy as np


class ShipState:
    def __init__(self, x=0, y=0, isVertical=False, length=0, isSunk=False):
        self.x = x
        self.y = y
        self.length = length
        self.isVertical = isVertical
        self.isSunk = isSunk
        self.cells = set()
        for offset in range(length):
            _x, _y = x, y
            if self.isVertical:
                _y += offset
            else:
                _x += offset
            self.cells.add((_x, _y))


class GameState:
    def __init__(self, shipStatesA, shipStatesB):
        self.shipsA = shipStatesA
        self.shipsB = shipStatesB
        self.boardA = np.zeros((10, 10))
        self.boardB = np.zeros((10, 10))
        self.playerA = True

    def index(cell):
        x = int(cell[1:]) - 1
        y = ord(cell[0]) - 65
        return x, y

    def play(self, cell):
        board = self.boardA if self.playerA else self.boardB
        ships = self.shipsB if self.playerA else self.shipsA
        x, y = GameState.index(cell)
        is_hit = any([(x, y) in ship.cells for ship in ships])
        if not is_hit:
            board[x, y] = -1
            self.playerA = not self.playerA
        else:
            board[x, y] = 1
            for ship in ships:
                if (x, y) in ship.cells:
                    is_sunk = True
                    for cell in ship.cells:
                        if board[cell] == 0:
                            is_sunk = False
                            break
                    ship.is_sunk = is_sunk

    def show(self, debug=False):
        empty = "~ "
        miss = "+ "
        hit = "X "
        ship = "O " if debug else "~ "
        print("  1 2 3 4 5 6 7 8 9 10  |     1 2 3 4 5 6 7 8 9 10")
        coordsA, coordsB = set(), set()
        for index in range(len(self.shipsA)):
            for cell in self.shipsA[index].cells:
                coordsA.add(cell)
            for cell in self.shipsB[index].cells:
                coordsB.add(cell)
        letter = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        for y in range(10):
            left = letter[y] + " "
            right = letter[y] + " "
            for x in range(10):
                a = self.boardA[x, y]
                if a < 0:
                    left += miss
                elif a > 0:
                    left += hit
                elif (x, y) in coordsB:
                    left += ship
                else:
                    left += empty
                b = self.boardB[x, y]
                if b < 0:
                    right += miss
                elif b > 0:
                    right += hit
                elif (x, y) in coordsA:
                    right += ship
                else:
                    right += empty
            print(left + "  |   " + right)
