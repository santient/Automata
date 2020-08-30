import os
import numpy as np
from automata import *

def print_board(board):
    string = "  "
    for j in range(board.cols):
        string += format(j, "x")
        if j < board.cols - 1:
            string += " "
        else:
            string += "\n"
    for i in range(board.rows):
        if i == board.rows // 2:
            string += "  " + "\u254c\u254c" * board.cols + "\n"
        if i > 0 and i < board.rows - 1:
            string += format(i - 1, "x") + " "
        else:
            string += "  "
        for j in range(board.cols):
            if i == 0 or i == board.rows - 1:
                if board[i, j] is not None and board[i, j].state == "alive":
                    string += "\u25a3"
                else:
                    string += "\u25a9"
            else:
                if board[i, j] is not None and board[i, j].state == "alive":
                    string += "\u25a0"
                else:
                    string += "\u25a1"
            string += " "
        string += "\n"
    print(string)

def print_cells(board):
    string = ""
    for i in range(1, board.rows - 1):
        for j in range(board.cols):
            if board[i, j] is not None and board[i, j].state == "alive":
                cell = board[i, j]
                string += "(Position: {:x} {:x}) ".format(cell.position[0] - 1, cell.position[1])
                string += "(Player: {}) ".format(cell.player)
                string += "(Rules: {})".format(", ".join(["".join(filter(None, [["up", "down", "left", "right"][idx] + " {} ".format(c) if c is not None else "" for idx, c in enumerate(rule.condition)])) + ("copy {} {}".format(rule.target, rule.destination) if isinstance(rule, Copy) else "delete {}".format(rule.target)) for rule in cell.rules]))
                string += "\n"
    print(string)

def print_all(board):
    print_board(board)
    print_cells(board)

valid_directions = ["up", "down", "left", "right"]
valid_targets = ["self", "up", "down", "left", "right"]
valid_states = ["alive", "dead"]

if __name__ == "__main__":
    board = Board(18, 16)
    while True:
        for player in range(1, 3):
            os.system("clear")
            print_all(board)
            print("Player {}, enter your move or leave blank to pass.".format(player))
            while True:
                coords = input("Coordinates: ")
                if not coords:
                    break
                coords = coords.split(" ")
                if len(coords) == 2:
                    try:
                        coords = (int(coords[0], 16) + 1, int(coords[1], 16))
                    except ValueError:
                        coords = None
                    half = board.rows // 2 - 1
                    if coords is not None and len(coords) == 2 and in_bounds(board, coords) and coords[0] >= 1 + (player - 1) * half and coords[0] < half + 1 + (player - 1) * half and (board[coords] is None or board[coords].player == player):
                        rule = input("Rule: ")
                        if not rule:
                            if board[coords] is None:
                                board[coords] = Cell(coords, [], "copy", player)
                                break
                            elif board[coords].player == player:
                                break
                        rule = rule.split(" ")
                        if len(rule) > 1 and rule[-2] == "delete":
                            condition = rule[:-2]
                            action = rule[-2:]
                        elif len(rule) > 2 and rule[-3] == "copy":
                            condition = rule[:-3]
                            action = rule[-3:]
                        else:
                            condition = None
                            action = None
                        if action is not None and condition is not None and len(condition) % 2 == 0:
                            cond = [None] * 4
                            for idx in range(0, len(condition), 2):
                                direction = condition[idx]
                                if direction not in valid_directions:
                                    cond = None
                                    break
                                state = condition[idx + 1]
                                if state not in valid_states:
                                    cond = None
                                    break
                                cond[valid_directions.index(direction)] = state
                            if cond is not None:
                                condition = cond
                                if action[0] == "delete" and action[1] in valid_targets:
                                    rule = Delete(condition, action[1])
                                elif action[0] == "copy" and action[1] in valid_targets and action[2] in valid_targets:
                                    rule = Copy(condition, action[1], action[2])
                                else:
                                    rule = None
                                if rule is not None:
                                    if board[coords] is None:
                                        board[coords] = Cell(coords, [rule], "copy", player)
                                        break
                                    elif board[coords].player == player:
                                        board[coords].rules.append(rule)
                                        break
                print("Invalid move.")
        board.step()
        for j in range(board.cols):
            if board[0, j] is not None and not board[0, j].permanent:
                if board[0, j].player == 2:
                    board[0, j].permanent = True
                    board[0, j].rules = []
                else:
                    board[0, j] = None
            if board[-1, j] is not None and not board[-1, j].permanent:
                if board[-1, j].player == 1:
                    board[-1, j].permanent = True
                    board[-1, j].rules = []
                else:
                    board[-1, j] = None
        if all(board[0, j] is not None for j in range(board.cols)):
            os.system("clear")
            print_all(board)
            print("Player 2 wins!")
            break
        if all(board[-1, j] is not None for j in range(board.cols)):
            os.system("clear")
            print_all(board)
            print("Player 1 wins!")
            break
