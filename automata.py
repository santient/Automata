from abc import ABC, abstractmethod
import numpy as np

class Cell():
    def __init__(self, position, rules=[], state="alive", player=None, permanent=False, replacement=None):
        self.position = position
        self.rules = rules
        self.state = state
        self.player = player
        self.permanent = permanent
        self.replacement = replacement

    def step(self, board):
        for rule in self.rules:
            rule.execute(board, self.position)

class Rule(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, board, position):
        pass

class Board():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = []
        self.array = np.full((rows, cols), None)

    def __getitem__(self, position):
        return self.array[position[0], position[1]]

    def __setitem__(self, position, cell):
        if self.array[position] is not None:
            self.cells.remove(self.array[position])
            self.array[position] = None
        if cell is not None:
            self.cells.append(cell)
            self.array[position] = cell

    def step(self):
        for cell in self.cells[:]:
            cell.step(self)
        for cell in self.cells[:]:
            if cell.state == "alive":
                cell.replacement = None
            elif cell.state == "dead":
                if cell.replacement is not None:
                    if cell.replacement.state == "conflict":
                        cell.replacement = None
                    elif cell.replacement.state == "copy":
                        cell.replacement.state = "alive"
                self[cell.position] = cell.replacement
            elif cell.state == "copy":
                cell.state = "alive"
            elif cell.state == "conflict":
                self[cell.position] = None

def condition_met(condition, board, position):
    positions = [(position[0] - 1, position[1]), (position[0] + 1, position[1]), (position[0], position[1] - 1), (position[0], position[1] + 1)]
    for p, c in zip(positions, condition):
        if c == "alive":
            if not in_bounds(board, p) or board[p] is None or board[p].state != "alive":
                return False
        elif c == "dead":
            if in_bounds(board, p) and board[p] is not None and board[p].state == "alive":
                return False
    return True

def in_bounds(board, position):
    return position[0] >= 0 and position[0] < board.rows and position[1] >= 0 and position[1] < board.cols

class Copy():
    def __init__(self, condition, target, destination):
        self.condition = condition
        self.target = target
        self.destination = destination

    def execute(self, board, position):
        if condition_met(self.condition, board, position):
            if self.target == "self":
                target_position = position
            elif self.target == "up":
                target_position = (position[0] - 1, position[1])
            elif self.target == "down":
                target_position = (position[0] + 1, position[1])
            elif self.target == "left":
                target_position = (position[0], position[1] - 1)
            elif self.target == "right":
                target_position = (position[0], position[1] + 1)
            if in_bounds(board, target_position) and board[target_position] is not None and board[target_position].state in ["alive", "dead"]:
                if self.destination == "self":
                    destination_position = position
                elif self.destination == "up":
                    destination_position = (position[0] - 1, position[1])
                elif self.destination == "down":
                    destination_position = (position[0] + 1, position[1])
                elif self.destination == "left":
                    destination_position = (position[0], position[1] - 1)
                elif self.destination == "right":
                    destination_position = (position[0], position[1] + 1)
                if in_bounds(board, destination_position):
                    if board[destination_position] is None:
                        board[destination_position] = Cell(destination_position, board[target_position].rules, "copy", board[position].player)
                    else:
                        if board[destination_position].state == "copy":
                            board[destination_position].state = "conflict"
                        elif board[destination_position].state in ["alive", "dead"]:
                            if board[destination_position].replacement is None:
                                board[destination_position].replacement = Cell(destination_position, board[target_position].rules, "copy", board[position].player)
                            else:
                                board[destination_position].replacement.state = "conflict"

class Delete():
    def __init__(self, condition, target):
        self.condition = condition
        self.target = target

    def execute(self, board, position):
        if condition_met(self.condition, board, position):
            if self.target == "self":
                target_position = position
            elif self.target == "up":
                target_position = (position[0] - 1, position[1])
            elif self.target == "down":
                target_position = (position[0] + 1, position[1])
            elif self.target == "left":
                target_position = (position[0], position[1] - 1)
            elif self.target == "right":
                target_position = (position[0], position[1] + 1)
            if in_bounds(board, target_position) and board[target_position] is not None and board[target_position].state == "alive" and not board[target_position].permanent:
                board[target_position].state = "dead"
