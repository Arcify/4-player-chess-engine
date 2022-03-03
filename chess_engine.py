# -*- coding: utf-8 -*-
"""
@Author: Arcify
"""
import random
import pygame as p
import time
import numpy as np


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

    def get_color(self):
        """
        Returns the color of the player.
        
        Args:
            None
            
        Returns:
            color (str): The color of the player
        """
        return self.color

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
                        else:  # there is a queen piece on this row/column
                            board.piece_locations[Position(row, column)] = Queen("Q", color, allies)
                    elif row == 7 or column == 7:
                        if color in "redgreen":
                            board.piece_locations[Position(row, column)] = King("K", color, allies)
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

    def play(self, moves):
        """
        Asks which move the player wants to play and returns it.
        
        Args:
            moves (arr): The array of possible moves
        
        Returns:
            (str): The move played
        """
        try:
            return input(self.name + " ('" + self.color + "'): Which move do you want to play?")
        except ValueError:
            raise ValueError("ValueError")


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
            start_time = time.time()
            self.alpha_beta(board, 4, 4, float('-inf'), float('inf'))
            end_time = time.time() - start_time
            print("Execution time: ", end_time)
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
        for move in board.legal_moves:
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

    def monte_carlo(self, board):
        root = Node(board)
        nr_iter = 100
        for i in range(nr_iter):
            expanded_node = self.expansion(root)
            reward, node = self.rollout(expanded_node)
            self.backpropogation(node, reward)
        return board.legal_moves[np.argmax([node.get_score() for node in root.children])] # return move with highest score

    def expansion(self, node):
        if not node.children: # when there are no known child nodes, we want to choose this node
            return node
        max_expl_scr = float('-inf')
        child_selected = None
        for child in node.children: # give each child node a UCB (exploration) score and choose the highest scoring child
            expl_scr = self.explore_score(child)
            if expl_scr > max_expl_scr:
                max_expl_scr = expl_scr
                child_selected = child
        return self.expansion(child_selected)

    def rollout(self, node):
        node.board.get_moves()
        if node.board.is_game_over():
            # if node.won():
            #     return (1, node)
            # elif node.lose():
            #     return (-1, node)
            # else:
            #     return (0.5, node)
            return (node.board.current_player, node) # the code is written such that the game always finishes at the losing player
                                                     # thus we return the player that loses together with the state (node)
        node.children = [Node(node.board.simulate(move), parent=node) for move in node.board.legal_moves]
        # all possible moves from the 'node' are simulated and added as child nodes (this could be wrong)
        random_child = random.choice(node.children)
        # we randomly pick one of the possible child nodes and keep going until the game is over
        return self.rollout(random_child)

    def backpropogation(self, node, losing_player):
        if self.color in "redyellow" and losing_player == 1 or losing_player == 3:
            reward = 1 # when the player that loses is either 1 (blue) or 3 (green) and the current player is red or yellow, we win
        elif self.color in "bluegreen" and losing_player == 0 or losing_player == 2:
            reward = 1 # when the player that loses is either 0 (red) or 2 (yellow) and the current player is blue or green. we also win
        else: # if either is not the case, the player that called the function lost
            reward = -1

        while node.parent is not None: # pass the reward up to all nodes that led to this outcome
            if reward == -1:
                node.loses += 1
            if reward == 1:
                node.wins += 1
            node.visits += 1
            node = node.parent

    def explore_score(self, node): #UCB (upper confident bound) score to calculate whether to exlore or a certain node
        score = node.get_score()
        return score + 2 * (np.sqrt(np.log(node.parent.visits + np.e + (10**-6))/(score + (10**-10))))


class Node(): #node used in the MCTS algorithm, storing the board, children, parent, wins, loses and visits
    def __init__(self, board, parent=None):
        self.board = board
        self.children = []
        self.parent = parent
        self.wins = 0
        self.loses = 0
        self.visits = 0

    def get_score(self): #score used to calculate which child node of the root node leads to the best results
        return self.wins - self.loses


class Board():
    """
    The class for the board state. Contains the representation of the board and
    has methods to perform actions on the board.
    """

    def __init__(self, dimension, players, locations, current_player):
        """
        Initializes the board of the game.
        
        Args:
            dimension: the area of the board
            players: the 4 players playing the game
            locations: the locations of the pieces
            current_player: the player that has to make the next move
            
        Returns:
            None
        """
        self.dimension = dimension
        self.sq_size = 504 // dimension
        self.piece_locations = locations  # storing the piece locations as a hashmap
        self.legal_moves = []
        self.players = players
        self.current_player = current_player  # red always plays the first move

    def get_current_player(self):
        return self.players[self.current_player]

    def show_board(self):
        """
        Returns the board formatted as a string.
        
        Args: None
        
        Returns:
            board (str): The board represented by letters, dashes, asterisks and numbers
        """
        p.init()
        display = p.display.set_mode(size=(504 + 250, 504))
        display.fill(p.Color("black"))
        clock = p.time.Clock()
        colors = [p.Color("white"), p.Color("gray")]
        for row in range(14):
            for column in range(14):
                if (self.is_on_board(Position(row, column))):
                    color = ((row + column) % 2)
                    color = colors[color]
                    p.draw.rect(display, color, p.Rect(column * (504 // 14), row * (504 // 14), 504 // 14, 504 // 14))
                    piece = self.check_for_piece(Position(row, column))
                    if piece is not None:
                        image = p.transform.scale(p.image.load("images/" + piece.color +
                                                               piece.piece_name + ".png"), (self.sq_size, self.sq_size))
                        display.blit(image,
                                     p.Rect(column * self.sq_size, row * self.sq_size, self.sq_size, self.sq_size))

        clock.tick(15)
        p.display.flip()

    def remove_piece(self, position):
        """
        Checks whether there are any pieces on the specified position
        and removes the piece if there is.
        
        Args:
            position (Pos): The specified position that has to be checked
        
        Returns:
            removed (Piece): the removed piece on the specified position
        """
        try:
            removed_piece = self.piece_locations.pop(position)
        except:
            removed_piece = None
        return removed_piece

    def check_for_piece(self, position):
        """
        Checks whether there are any pieces on a specified position and returns
        the piece if there is.
        
        Args:
            position(Pos): The specified position that has to be checked
            
        Returns:
            piece (Piece): the piece on the specified position
        """
        return self.piece_locations.get(position)

    def is_on_board(self, position):
        """
        Checks whether the specified position is located on the chess board.
        
        Args:
            position (Pos): The specified position
            
        Returns (bool):
            Whether or not the position is located on the chess board
        """
        if (((3 <= position.get_x() <= 10) and (0 <= position.get_y() <= 13)) or
                (0 <= position.get_x() < 3 <= position.get_y() <= 10) or
                (13 >= position.get_x() > 10 >= position.get_y() >= 3)):
            return True
        else:
            return False

    def getmove(self, position, xm, ym):
        """
        Returns a new position derived from the current position and a direction
        existing of an x direction and a y direction.
        
        Args:
            xm (int): The x direction
            ym (int): The y direction
            
        Returns (Pos):
            The new position
        """
        new_x = position.x + xm
        new_y = position.y + ym
        return Position(new_x, new_y)
        # new position because we do not want to change the position of the piece

    def make_move(self, move):
        """
        Moves a piece from a start position to an end position and removes 
        the piece located at the end position.
        
        Args:
            move (Move): The move that is carried out
            
        Returns: 
            removed_piece (Piece): The piece that is removed
        """
        removed_piece = self.remove_piece(move.get_end_position())
        new_end_pos = Position(move.end_position.get_x(), move.end_position.get_y())
        self.piece_locations[new_end_pos] = self.piece_locations.pop(move.get_start_position())
        return removed_piece

    def undo_move(self, move, removed_piece):
        """
        Moves a piece from an end position to a start position and puts the piece
        that has been removed back into place
        
        Args:
            move (Move): The move that was carried out
            removed_piece (Piece): The piece that was removed
            
        Returns:
            None
        """
        target_pos = Position(move.end_position.get_x(), move.end_position.get_y())
        orig_pos = Position(move.start_position.get_x(), move.start_position.get_y())
        # start position of move is the initial position of the piece before moving
        self.piece_locations[orig_pos] = self.piece_locations.pop(move.get_end_position())
        if removed_piece is not None:
            self.piece_locations[target_pos] = removed_piece

    def get_moves(self):
        """
        Iterates through all the pieces and adds for each piece the possible moves
        to the list

        Args: None
            
        Returns: None
        """
        in_check, pin_info, check_info = self.check_info()
        for pos in self.piece_locations.keys():
            if self.piece_locations[pos].get_color() == self.players[self.current_player].get_color():
                if in_check:
                    if len(check_info) == 1:
                        if self.piece_locations[check_info[0][0]].get_piece_name() == "N":
                            self.legal_moves.append(Move(pos, check_info[0][0]))
                        else:
                            poss_positions = self.block_or_capture(check_info)
                            self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos, poss_positions=poss_positions)
                    elif self.piece_locations[pos].get_piece_name() == "K":
                        self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos)
                else:
                    self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos, pin_info=pin_info)
        return self.legal_moves

    def block_or_capture(self, check_info):
        possible_positions = []
        for tiles in range(1, 13):
            square = Position(self.get_king_pos().get_x() + check_info[0][1][0] * tiles, self.get_king_pos().get_y() + check_info[0][1][1] * tiles)
            possible_positions.append(square)
            if square == check_info[0][0]:
                return possible_positions

    def check_info(self):
        """
        returns which enemy pieces are checking the king and which friendly pieces are blocking checks (pins)

        Args: None

        Returns: (tuple): whether the king is in check, which pieces are pinned and which pieces are delivering the check

        Credits: This function has been inspired from Eddie Sharicks' youtube tutorial which can be found here:
        https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_
                """
        in_check = False
        check_info = []
        pin_info = {}
        position = self.get_king_pos()
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for k in range(len(directions)):
            direction = directions[k]
            possible_pin = ()
            for tile in range(1, 13):
                end_position = self.getmove(position, direction[0] * tile, direction[1] * tile)
                if self.is_on_board(end_position):
                    piece = self.check_for_piece(end_position)
                    if piece is not None:
                        if self.get_current_player().get_color() in piece.get_allied_colors():
                            if possible_pin == ():
                                possible_pin = (end_position, direction)
                            else:
                                break
                        elif self.get_current_player().get_color() not in piece.get_allied_colors():
                            if self.possible_check(k, tile, piece, direction):
                                if possible_pin == ():
                                    in_check = True
                                    check_info.append((end_position, direction))
                                    break
                                else:
                                    pin_info[piece] = possible_pin
                                    break
                            else:
                                break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_pos = self.getmove(position, m[0], m[1])
            if self.is_on_board(end_pos):
                poss_piece = self.check_for_piece(end_pos)
                if poss_piece is not None:
                    if self.get_current_player().get_color() not in poss_piece.get_allied_colors():
                        if poss_piece.get_piece_name() == "N":
                            in_check = True
                            check_info.append((end_pos, m))
        return in_check, pin_info, check_info

    def possible_check(self, k, tile, piece, direction):
        if 0 <= k <= 3 and piece.get_piece_name() == "R":
            return True
        elif 4 <= k <= 7 and piece.get_piece_name() == "B":
            return True
        elif tile == 1 and piece.get_piece_name() == "P":
            if piece.diag_left_direction == (-direction[0], -direction[1]) or \
                    (piece.diag_right_direction == (-direction[0], -direction[1])):
                return True
        elif piece.get_piece_name() == "Q":
            return True
        elif tile == 1 and piece.get_piece_name() == "K":
            return True
        else:
            return False

    def get_king_pos(self):
        for pos in self.piece_locations.keys():
            piece = self.piece_locations[pos]
            if piece.get_color() == self.get_current_player().get_color() and piece.get_piece_name() == 'K':
                return pos

    def switch_players(self):
        """
        Switches the current player to the player which turn it is next
        
        Args:
            None
            
        Returns:
            None
        """
        if self.current_player < 3:
            self.current_player += 1
        else:
            self.current_player = 0

    def score(self):
        score = 0
        for piece in self.piece_locations.values():
            if self.players[self.current_player].get_color() in piece.get_allied_colors():
                score += piece.get_score()
            else:
                score -= piece.get_score()

        return score

    def simulate(self, move, switch = True):
        new_board = Board(14, self.players, self.piece_locations.copy(), self.current_player)
        # not sure if doing a shallow copy will cause problems later on
        new_board.make_move(move)
        if switch:
            new_board.switch_players()
            new_board.get_moves()
        return new_board

    def is_game_over(self):
        game_finished = False
        if len(self.legal_moves) == 0:
            check, pin_info, check_info = self.check_info()
            if check:
                print(str(self.current_player) + " got checkmated!")
            else:
                print("A stalemate has occurred!")
            print(":)")
            game_finished = True
        return game_finished


class Move(object):
    """
    The class for a move. Contains the start and end position of a move, and
    the name of the move.
    """

    def __init__(self, start_position, end_position):
        """
        Initializes a move by setting the start, end and name of the move.
        
        Args:
            start_position (Pos): The start position of the moved piece
            end_position (Pos): The end position of the moved piece
            
        Returns:
            None
        """
        self.start_position = start_position
        self.end_position = end_position
        self.move_name = self.get_notation()

    def get_notation(self):
        """
        Converts the row and column of the start and end position to chess notation
        consisting out of letters for the columns (files) and numbers for the rows (ranks).
        
        Args:
            None
        
        Returns:
            notation (str): The move written in chess notation
        """
        notation = ""
        ranks = {i: (14 - i) for i in reversed(range(0, 14))}
        files = {i: chr(i + 97) for i in range(14)}
        notation += files[self.start_position.get_y()]
        notation += str(ranks[self.start_position.get_x()])
        notation += files[self.end_position.get_y()]
        notation += str(ranks[self.end_position.get_x()])
        return notation

    def get_end_position(self):
        """
        Returns the end position of the move.
        
        Args:
            None
            
        Returns:
            end_position (Pos): The end position of the moved piece
        """
        return self.end_position

    def get_start_position(self):
        """
        Returns the start position of the move.
        
        Args:
            None
            
        Returns:
            start_position (Pos): The start position of the moved piece
        """
        return self.start_position

    def get_move_name(self):
        return self.move_name

    def __eq__(self, other):
        return self.move_name == other.move_name


class Position(object):
    """
    The class for a position. Contains an x and a y coordinate representing the 
    row/column of the board.
    """

    def __init__(self, x, y):
        """
        Initializes a position by setting the x and y coordinates.
        
        Args:
            x (int): The row of the position
            y (int): The column of the position
            
        Returns:
            None
        """
        self.x = x
        self.y = y

    def __eq__(self, other):
        """
        Compares whether two positions are equal.
        
        Args:
            other (Pos): The position that is used to compare with
        
        Returns (bool):
            Whether or not the positions are the same
        """
        if not isinstance(other, self.__class__):
            return False
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def set_x(self, x):
        """
        Sets the x coordinate of the position
        
        Args:
            x (int): The x coordinate
            
        Returns:
            None
        """
        self.x = x

    def set_y(self, y):
        """
        Sets the y coordinate of the position
        
        Args:
            y (int): The y coordinate
            
        Returns:
            None
        """
        self.y = y

    def get_x(self):
        """
        Returns the x coordinate of the position
        
        Args:
            None
            
        Returns:
            x (int): The x coordinate
        """
        return self.x

    def get_y(self):
        """
        Returns the y coordinate of the position
        
        Args:
            None
            
        Returns:
            y (int): The y coordinate
        """
        return self.y


class Piece(object):
    """
    The interface class for different pieces. It stores the position, name, color and
    allied colors of the piece. And it provides multiple functions to interact with
    the pieces.
    """

    def __init__(self, piece_name, color, allied_colors):
        """
        Initializes a piece by setting the position, name, color and allied colors
        of the piece.
        
        Args:
            piece_name (str): The name of piece consisting out of a capital letter
            color (str): The color of the piece
            allied_collors (str): The colors of the current piece and the allied pieces
            
        Returns:
            None
        """
        self.piece_name = piece_name
        self.color = color
        self.allied_colors = allied_colors

    def __str__(self):
        """
        Returns the name of the piece displayed as the color of the piece
        
        Args:
            None
            
        Returns (str):
            The name of the piece displayed in the color of the piece
        """
        return " " + self.piece_name + " "

    def get_legal_moves(self):
        """
        Interface method to get all possible moves for a certain piece
        """
        pass

    def get_allied_colors(self):
        """
        Returns the allied colors of the piece
        
        Args:
            None
            
        Returns:
            allied_colors (str): The allied colors of the piece
        """
        return self.allied_colors

    def get_color(self):
        """
        Returns the color of the piece
        
        Args:
            None
            
        Returns:
            color (str): The color of the piece
        """
        return self.color

    def get_piece_name(self):
        """
        Returns the name of the piece
        
        Args:
            None
            
        Returns:
            piece_name (str): The name of the piece existing out of a capital letter
        """
        return self.piece_name

    def get_score(self):
        pass


class Pawn(Piece):
    """
    The class for the Pawn piece. It sets the position, piece_name, color, 
    direction, diag_left_direction, diag_right_direction, allied_colors and start_position
    of the piece.
    """

    def __init__(self, piece_name, color, direction, diag_left_direction,
                 diag_right_direction, allied_colors, start_position):
        """
        Initializes the pawn.
        
        Args:
            position (Pos): The position of the pawn
            piece_name (str): The name of the piece existing out of a capital letter
            color (str): The color of the pawn
            direction (tuple): Direction a pawn moves to consisting of an x and an y value
            diag_left_direction (tuple): Direction of a pawn when capturing diagonal to the left
            diag_right_direction (tuple): Direction of a pawn when capturing diagonal to the right
            allied_colors (str): The allied colors of the pawn
            start_position (Pos): The initial position of the pawn
            
        Returns:
            None
        """
        super(Pawn, self).__init__(piece_name, color, allied_colors)
        self.direction = direction
        self.diag_left_direction = diag_left_direction
        self.diag_right_direction = diag_right_direction
        self.start_position = start_position

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible pawn moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        end_position = board.getmove(position, self.direction[0], self.direction[1])
        # when the pawn moves forward 1 square
        end_position_two_squares = board.getmove(position, self.direction[0] * 2, self.direction[1] * 2)
        # when the pawn moves forward two squares (only allowed at the start position)
        end_position_diag_left = board.getmove(position, self.diag_left_direction[0], self.diag_left_direction[1])
        # when the pawn can capture a piece diagonal to the left
        end_position_diag_right = board.getmove(position, self.diag_right_direction[0], self.diag_right_direction[1])
        pin_direction = None
        if pin_info is not None:
            if self in pin_info:
                pin_direction = pin_info[self][1]
        # when the pawn can capture a piece diagonal to the right
        if board.is_on_board(end_position):
            if board.check_for_piece(end_position) == None:  # no piece infront of pawn
                if poss_positions is None or end_position in poss_positions:
                    if pin_direction is None or pin_direction == (self.direction[0], self.direction[1]) or pin_direction == (-self.direction[0], -self.direction[1]):
                        moves.append(Move(position, end_position))
                        if poss_positions is None or end_position in poss_positions:
                            if (self.start_position == position) and \
                                board.check_for_piece(end_position_two_squares) is None:
                                # no piece in either of two squares in front of pawn
                                moves.append(Move(position, end_position_two_squares))
            if board.check_for_piece(end_position_diag_left) is not None:
                if board.check_for_piece(end_position_diag_left).get_color() not in self.allied_colors:
                    # enemy piece diagonal to the left
                    if poss_positions is None or end_position_diag_left:
                        if pin_direction is None or pin_direction == (self.diag_left_direction[0], self.diag_left_direction[1]) or \
                            pin_direction == (-self.diag_left_direction[0], -self.diag_left_direction[1]):
                            moves.append(Move(position, end_position_diag_left))
            if board.check_for_piece(end_position_diag_right) is not None:
                if board.check_for_piece(end_position_diag_right).get_color() not in self.allied_colors:
                    # enemy piece diagonal to the right
                    if poss_positions is None or end_position_diag_right in poss_positions:
                        if pin_direction is None or pin_direction == (
                        self.diag_right_direction[0], self.diag_right_direction[1]) or \
                                pin_direction == (-self.diag_right_direction[0], -self.diag_right_direction[1]):
                            moves.append(Move(position, end_position_diag_right))
        return moves

    def get_score(self):
        return 1


class Knight(Piece):
    """
    The class for the Knight piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible knight moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # all possible knight moves
        for direction in directions:
            end_position = board.getmove(position, direction[0], direction[1])
            if poss_positions is None or end_position in poss_positions:
                if board.is_on_board(end_position):
                    if board.check_for_piece(end_position) is None:  # no piece on end position
                        moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            # enemy piece on end position
                            moves.append(Move(position, end_position))

        return moves

    def get_score(self):
        return 3


class Bishop(Piece):
    """
    The class for the Bishop piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible bishop moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        pin_direction = None
        if pin_info is not None:
            if self in pin_info:
                pin_direction = pin_info[self][1]
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        # all possible bishop directions
        for direction in directions:
            for tiles in range(1, 10):  # maximum possible amount of diagonal squares in a row
                end_position = board.getmove(position, direction[0] * tiles, direction[1] * tiles)
                # position tiles amount diagonal of the bishop
                if board.is_on_board(end_position):
                    if board.check_for_piece(end_position) == None:
                        if poss_positions is None or end_position in poss_positions:
                            if pin_direction is None or direction == pin_direction or (
                            -direction[0], -direction[1]) == pin_direction:
                                moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            if poss_positions is None or end_position in poss_positions:
                                if pin_direction is None or direction == pin_direction or (
                                -direction[0], -direction[1]) == pin_direction:
                                    moves.append(Move(position, end_position))
                            break  # can not jump over enemy piece but can capture
                        else:
                            break  # cant jump over allied piece and can't capture
                else:
                    break

        return moves

    def get_score(self):
        return 5


class Rook(Piece):
    """
    The class for the Rook piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible rook moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        pin_direction = None
        if pin_info is not None:
            if self in pin_info:
                pin_direction = pin_info[self][1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        # all possible rook directions
        for direction in directions:
            for tiles in range(1, 13):  # maximum possible amount of straight squares in a row
                end_position = board.getmove(position, direction[0] * tiles, direction[1] * tiles)
                # position tiles amount straight of the rook
                if board.is_on_board(end_position):
                    if board.check_for_piece(end_position) is None:
                        if poss_positions is None or end_position in poss_positions:
                            if pin_direction is None or direction == pin_direction or (
                            -direction[0], -direction[1]) == pin_direction:
                                moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            if poss_positions is None or end_position in poss_positions:
                                if pin_direction is None or direction == pin_direction or (
                                        -direction[0], -direction[1]) == pin_direction:
                                    moves.append(Move(position, end_position))
                            break  # can't jump over enemy piece but can capture
                        else:
                            break  # can't jump over allied piece and can't capture
                else:
                    break

        return moves

    def get_score(self):
        return 5


class King(Piece):
    """
    The class for the King piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible king moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            position (Pos):
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        # all possible king moves
        for direction in directions:
            end_position = board.getmove(position, direction[0], direction[1])
            # end position of a certain direction of the king
            if board.is_on_board(end_position):
                in_check, pin_info, check_info = board.simulate(Move(position, end_position), switch = False).check_info()
                if not in_check:
                    if board.check_for_piece(end_position) is None:
                        moves.append(Move(position, end_position))
                        # no pieces on position thus can move king to end position
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            # can capture enemy piece thus can move king to end position
                            moves.append(Move(position, end_position))
        return moves

    def get_score(self):
        return 0


class Queen(Piece):
    """
    The class for the Queen piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions = None, pin_info = None):
        """
        Adds all the possible queen moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        Rook.get_legal_moves(self, board, moves, position, poss_positions, pin_info)
        Bishop.get_legal_moves(self, board, moves, position, poss_positions, pin_info)
        # because the queen can move in the same directions as the rook and bishop combined
        return moves

    def get_score(self):
        return 9


class FourPlayerChess(object):
    """
    The class that implements the game. It contains the control loop of 
    one round of the game and multiple functions associated with moving the pieces
    """

    def __init__(self):
        """
        Initializes the FourPlayerChess class by creating arrays of the possible moves
        and all the pieces and creating the 4 players of the game and creating the board
        and the current player.
        
        Args:
            None
            
        Returns:
            None
        """
        answer = input("Would you like to play against the computer[y][n] ")
        if answer == 'y':
            while (True):
                algorithm = input(
                    "Choose the algorithm to be used: \n1 = Random 2 = Alpha-Beta 3 = MonteCarlo 4 = Neural Network\n")
                if algorithm in ("1", "2", "3", "4"):
                    break
            players = [RandomComputerPlayer("red", algorithm), RandomComputerPlayer("blue", algorithm),
                       RandomComputerPlayer("yellow", algorithm), RandomComputerPlayer("green", algorithm)]
        else:
            players = [HumanPlayer("red"), HumanPlayer("blue"), HumanPlayer("yellow"),
                       HumanPlayer("green")]
        self.board = Board(14, players, {}, 0)
        players[0].initialize_pieces((12, 14), (3, 11), "red", "redyellow", (-1, 0), (-1, -1), (-1, 1), self.board)
        players[1].initialize_pieces((3, 11), (0, 2), "blue", "bluegreen", (0, 1), (-1, 1), (1, 1), self.board)
        players[2].initialize_pieces((0, 2), (3, 11), "yellow", "redyellow", (1, 0), (1, 1), (1, -1), self.board)
        players[3].initialize_pieces((3, 11), (12, 14), "green", "bluegreen", (0, -1), (1, -1), (-1, -1), self.board)

    def play(self):
        """
        The method that starts the game and handles the rounds until the game 
        ends which happens when either a checkmate or a stalemate occurs.
        
        Args:
            None
            
        Returns:
            None
        """
        selected_tiles = []
        game_finished = False
        while not game_finished:
            self.board.show_board()
            if isinstance(self.board.get_current_player(), RandomComputerPlayer):
                self.board.get_moves()
                game_finished = self.board.is_game_over()
                if not game_finished:
                    self.AI_move()
                    self.board.legal_moves = []
                    self.board.switch_players()
            elif len(selected_tiles) == 2:
                game_finished = self.board.is_game_over()
                if not game_finished:
                    selected_tiles = self.player_move(selected_tiles)
                    if len(selected_tiles) == 0:
                        self.board.legal_moves = []
                        self.board.switch_players()
            for e in p.event.get():
                if e.type == p.QUIT:
                    game_finished = True
                elif e.type == p.MOUSEBUTTONDOWN:
                    selected_tiles = self.mouse_handler(selected_tiles)

    def AI_move(self):
        self.board.make_move(self.board.get_current_player().play(self.board))
        # print("Complexity: ", self.board.get_current_player().complexity)

    def player_move(self, selected_squares):
        move = Move(selected_squares[0], selected_squares[1])
        self.board.get_moves()
        if move in self.board.legal_moves:
            self.board.make_move(move)
            selected_squares = []
        else:
            selected_squares = [selected_squares[1]]
            print("Illegal move, try again!")
        return selected_squares

    def mouse_handler(self, selected_squares):
        mouse_pos = p.mouse.get_pos()
        col = mouse_pos[0] // self.board.sq_size
        row = mouse_pos[1] // self.board.sq_size
        if not self.board.is_on_board(Position(row, col)) or Position(row, col) in selected_squares:
            selected_squares = []
        else:
            selected_square = Position(row, col)
            selected_squares.append(selected_square)
        return selected_squares


if __name__ == "__main__":
    """
    The main control loop. Multiple games can be executed sequentially.
    """
    keep_playing = True
    game = FourPlayerChess()
    while keep_playing:
        game.play()
        answer = input("Do you want to play another game? [y/n] ")
        if answer != 'y':
            keep_playing = False
