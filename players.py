from helpers import Position
import random
import copy
import time
import numpy as np
from pieces import Knight, King, Queen, Rook, Bishop, Pawn


class Player(object):
    """
    The interface class for a player. It sets the name and color of a player,
    initializes the pieces and gets the move the player wants to play each round.
    """

    def __init__(self, color):
        """
        Initializes a player.

        Args:
            color (str): the color that is used by the player

        Returns:
            None
        """
        self.color = color
        self.allied_colors = "redyellow" if color in "redyellow" else "bluegreen"

    def get_color(self):
        """
        Returns the color of the player.

        Args: None

        Returns:
            color (str): The color of the player
        """
        return self.color

    def get_king_pos(self):
        return self.king

    def play(self):
        """
        Interface method to play a move
        """
        pass

    def initialize_pieces(self, x_range, y_range, color, allies, direction, diag_left, diag_right, board):
        """
        Initializes all the pieces of the player at the start of the game.

        Args:
            x_range (tuple): The start and end row of the outer loop
            y_range (tuple): The start and end column of the inner loop
            color (str): The color of a piece
            allies (str): The two colors of a team of two players
            direction (tuple): Direction a pawn moves to consisting of an x and an y value
            diag_left (tuple): Direction of a pawn when capturing diagonal to the left
            diag_right (tuple): Direction of a pawn when capturing diagonal to the right

        Returns:
            None
        """
        for row in range(x_range[0], x_range[1]):
            for column in range(y_range[0], y_range[1]):
                # because the board/pieces are symmetric I can specify which columns/rows
                # the pieces have to be placed on, besides the king/queen because they
                # are not symmetric
                if (row == 0 or row == 13) or (column == 0 or column == 13):
                    if (row == 3 or row == 10) or (column == 3 or column == 10):
                        board.piece_locations[Position(row, column)] = Rook("R", color, allies)
                    elif (row == 4 or row == 9) or (column == 4 or column == 9):
                        board.piece_locations[Position(row, column)] = Knight("N", color, allies)
                    elif (row == 5 or row == 8) or (column == 5 or column == 8):
                        board.piece_locations[Position(row, column)] = Bishop("B", color, allies)
                    elif row == 6 or column == 6:
                        if color in "blueyellow":  # then there is a king piece on this row/column
                            board.piece_locations[Position(row, column)] = King("K", color, allies)
                            board.king_positions[1 if color == "blue" else 2] = Position(row, column)
                        else:  # there is a queen piece on this row/column
                            board.piece_locations[Position(row, column)] = Queen("Q", color, allies)
                    elif row == 7 or column == 7:
                        if color in "redgreen":
                            board.piece_locations[Position(row, column)] = King("K", color, allies)
                            board.king_positions[0 if color == "red" else 3] = Position(row, column)
                        else:
                            board.piece_locations[Position(row, column)] = Queen("Q", color, allies)
                else:
                    board.piece_locations[Position(row, column)] = Pawn("P", color, direction, diag_left, diag_right,
                                                                        allies, Position(row, column))


class HumanPlayer(Player):
    """
    The class for a human player. It contains a method which returns which move
    the user plays and a function that sets the name of the player.
    """


class RandomComputerPlayer(Player):
    """
    The class for a computer player. It contains a method which returns a random
    move and a function to set the name of the computer player.
    """

    def __init__(self, color, algorithm):
        super().__init__(color)
        self.algorithm = algorithm
        self.best_move = None
        self.complexity = 0

    def play(self, board):
        """
        Randomly generates a legal move

        Args:
            board: the chess board

        Returns:
            (str): The name of the generated move
        """
        if self.algorithm == "1":
            print("----Generating random move for " + self.color + "-----")
            return board.legal_moves[random.randint(0, len(board.legal_moves) - 1)]
        elif self.algorithm == "2":
            self.alpha_beta(board, 4, 4, float('-inf'), float('inf'))
            return self.best_move
        elif self.algorithm == "3":
            return self.monte_carlo(board)

    def alpha_beta(self, board, depth, initial_depth, alpha, beta):
        self.complexity += 1
        if depth == 0:
            return board.score()

        if board.legal_moves is None:
            return board.score()
        best_score = float('-inf')
        ordered_moves = self.get_ordered_moves(board)
        for move in ordered_moves:
            score = -self.alpha_beta(board.simulate(move), depth - 1, initial_depth, -beta, -alpha)
            if score > best_score:
                best_score = score
                if depth == initial_depth:
                    self.best_move = move
            if best_score > alpha:
                alpha = best_score
            if alpha >= beta:
                break
        return best_score

    def get_ordered_moves(self, board):
        def order(move):
            return board.simulate(move, switch=False).score()

        in_order = sorted(board.legal_moves, key=order, reverse=True)
        return in_order

    def monte_carlo(self, board):
        root = Node(board)
        nr_iter = 1000
        for i in range(nr_iter):
            expanded_node = self.selection(root)
            reward = self.rollout(expanded_node)
            self.backpropogation(reward, expanded_node)
        return self.best_child(root).parent_action  # return move with the highest score

    def selection(self, node):
        current_node = node
        while not current_node.board.is_game_over():
            if not len(current_node.untried_actions) == 0:
                return self.expansion(current_node)
            else:
                current_node = self.best_child(current_node)
        return current_node

    def expansion(self, node):
        action = node.untried_actions.pop()
        child_node = Node(node.board.simulate(action), parent=node, action=action)
        node.children.append(child_node)
        return child_node

    def rollout(self, node):
        current_board = node.board
        iter = 0
        while not current_board.is_game_over():
            # current_board.show_board()
            if iter == 5:
                return self.result(current_board)
            action = random.choice(current_board.legal_moves)
            current_board = current_board.simulate(action)
            iter += 1
        return self.result(current_board)

    def backpropogation(self, reward, node):
        current_node = node
        while True:  # pass the reward up to all nodes that led to this outcome
            if reward == -1:
                current_node.loses += 1
            if reward == 1:
                current_node.wins += 1
            current_node.visits += 1
            current_node = current_node.parent
            if current_node is None:
                break

    def best_child(self, node):  # UCB (upper confident bound) score to calculate whether to explore or a certain node
        c_param = 0.1
        return node.children[np.argmax([(c.get_score() / c.visits) + c_param * np.sqrt((2 * np.log(node.visits) / c.visits))
                                        for c in node.children])]

    def result(self, board):
        plr = 1 if board.get_current_player().get_color() in self.allied_colors else -1
        if board.is_game_over():
            return plr * -1
        else:
            if board.score() > 0:
                return plr * 1
            else:
                return plr * -1


class Node:  # node used in the MCTS algorithm, storing the board, children, parent, wins, loses and visits
    def __init__(self, board, parent=None, action=None):
        self.board = board
        self.parent = parent
        self.parent_action = action
        self.children = []
        self.visits = 0
        self.wins = 0
        self.loses = 0
        self.untried_actions = copy.deepcopy(board.legal_moves)

    def get_score(self):  # score used to calculate which child node of the root node leads to the best results
        return self.wins - self.loses

    def get_visits(self):
        return self.visits