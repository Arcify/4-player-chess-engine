# -*- coding: utf-8 -*-
"""
@Author: Arcify
"""
import random
import pygame as p
import time

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
            pieces (arr): The array of pieces which we append the initialized pieces to
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
                #because the board/pieces are symmetric I can specify which columns/rows
                #the pieces have to be placed on, besides the king/queen because they
                #are not symmetric
                if (row == 0 or row == 13) or (column == 0 or column == 13):
                    if (row == 3 or row == 10) or (column == 3 or column == 10):
                        board.piece_locations[Position(row, column)] = Rook("R", color, allies)
                    elif (row == 4 or row == 9) or (column == 4 or column == 9):
                        board.piece_locations[Position(row, column)] = Knight("N", color, allies)
                    elif (row == 5 or row == 8) or (column == 5 or column == 8):
                        board.piece_locations[Position(row, column)] = Bishop("B", color, allies)
                    elif row == 6 or column == 6:
                        if color in "blueyellow": #then there is a king piece on this row/column
                            board.piece_locations[Position(row, column)] = King("K", color, allies)
                        else: #there is a queen piece on this row/column
                            board.piece_locations[Position(row, column)] = Queen("Q", color, allies)
                    elif row == 7 or column == 7:
                        if color in "redgreen":
                            board.piece_locations[Position(row, column)] = King("K", color, allies)
                        else:
                            board.piece_locations[Position(row, column)] = Queen("Q", color, allies)
                else:
                    board.piece_locations[Position(row, column)] = Pawn("P", color, direction, diag_left, diag_right, allies, Position(row, column))
                    
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
            moves (arr): The array of possible moves
            
        Returns:
            (str): The name of the generated move
        """
        if self.algorithm == "1":
            print("----Generating random move for " + self.color + "-----")
            moves = board.get_moves()
            return moves[random.randint(0, len(moves)-1)]
        elif self.algorithm == "2":
            start_time = time.time()
            self.alpha_beta(board, 4, 4, float('-inf'), float('inf'))
            end_time = time.time() - start_time
            print("Execution time: ", end_time)
            return self.best_move
    
    def alpha_beta(self, board, depth, initial_depth, alpha, beta):
        self.complexity += 1
        if depth == 0:
            return board.score()
        
        board.get_moves()
        if board.legal_moves == None:
            return board.score()
        best_score = float('-inf')
        for move in board.legal_moves:
            score = -self.alpha_beta(board.simulate(move), depth-1, initial_depth, -beta, -alpha)
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
        pass

    def selection(self, board):
        best_value = float('-inf')
        child_selected = None
        for move in board.legal_moves:
            child = board.simulate(move)
            value = child.score()
            if value > best_value:
                best_value = value
                child_selected = child
        return child_selected
        
class Board():
    """
    The class for the board state. Contains the representation of the board and
    has methods to perform actions on the board.
    """
    
    def __init__(self, dimension, players, locations, current_player):
        """
        Initializes the board of the game.
        
        Args:
            pieces (arr): The array of pieces that are present on the board
            
        Returns:
            None
        """
        self.dimension = dimension
        self.sq_size = 504 // dimension
        self.piece_locations = locations #storing the piece locations as a hashmap
        self.legal_moves = []
        self.players = players
        self.current_player = current_player #red always plays the first move
        
    def get_current_player(self):
        return self.players[self.current_player]
    
    
    def show_board(self):
        """
        Returns the board formatted as a string.
        
        Args:
            None
        
        Returns:
            board (str): The board represented by letters, dashes, asterisks and numbers
        """
        p.init()
        display = p.display.set_mode(size = (504 + 250, 504))
        display.fill(p.Color("black"))
        clock = p.time.Clock()
        colors = [p.Color("white"), p.Color("gray")]
        for row in range(14):
            for column in range(14):
                if(self.is_on_board(Position(row, column))):
                    color = ((row + column) % 2)
                    color = colors[color]
                    p.draw.rect(display, color, p.Rect(column*(504//14), row*(504//14), 504//14, 504//14))
                    piece = self.check_for_piece(Position(row, column))
                    if piece is not None:
                        image = p.transform.scale(p.image.load("images/" + piece.color + 
                                    piece.piece_name + ".png"),(self.sq_size, self.sq_size))
                        display.blit(image, p.Rect(column*self.sq_size, row*self.sq_size, self.sq_size, self.sq_size))
                
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
        if (((position.get_x() >= 3 and position.get_x() <= 10) and (0 <= position.get_y() <= 13)) or \
                (0 <= position.get_x() < 3 and 3 <= position.get_y() <= 10) or \
                    (10 < position.get_x() <= 13 and 3 <= position.get_y() <= 10)):
            return True
        else:
            return False
        
    def getmove(self, position, xm, ym):
        """
        Returns a new position derived from the current position and a direction
        existing of an x direction and a y direction.
        
        Args:
            xm (int): The x direction
            xy (int): The y direction
            
        Returns (Pos):
            The new position
        """
        new_x = position.x + xm
        new_y = position.y + ym
        return Position(new_x, new_y)
        #new position because we dont want to change the position of the piece
        
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
            #start position of move is the initial position of the piece before moving
        self.piece_locations[orig_pos] = self.piece_locations.pop(move.get_end_position())
        if removed_piece != None:
            self.piece_locations[target_pos] = removed_piece
    
    def get_moves(self):
        """
        Iterates through all the pieces and adds for each piece the possible moves
        to the list
        
        Args:
            None
            
        Returns:
            None
        """
        check = self.in_check()
        for pos in self.piece_locations.keys():
            if self.piece_locations[pos].get_color() == self.players[self.current_player].get_color():
                if check is not None:
                   self.legal_moves = self.block_check(check)
                else:
                    self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos)
        
    def block_check(self, check):
        valid_pos = []
        for tiles in range(1, 13):
            square = Position(check[1].get_x() + check[2][0] * tiles, check[1].get_y() + check[2][1] * tiles)
            valid_pos.append(square)
            if (square.get_x(), square.get_y()) == check[1]:
                return valid_pos
            
    def in_check(self):
        position = self.get_king_pos()
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for k in range(len(directions)):
            direction = directions[k]
            for tile in range(1, 13):
                end_position = self.getmove(position, direction[0] * tile, direction[1] * tile)
                if self.is_on_board(end_position):
                    piece = self.check_for_piece(end_position)
                    if piece != None:
                        if self.players[self.current_player].get_color() not in piece.get_allied_colors():
                            if 0 <= k <= 3 and piece.get_piece_name() == "R" or \
                                4 <= k <= 7 and piece.get_piece_name() == "B" or \
                                tile == 1 and piece.get_piece_name() == "P" and piece.direction is (-direction[0], -direction[1]) or\
                                    piece.get_piece_name() == "Q":
                                        return [end_position, position, direction, piece.get_piece_name()]
                        else:
                            break
        return None
                
                
    def get_king_pos(self):
        for pos in self.piece_locations.keys():
            piece = self.piece_locations[pos]
            if piece.get_color() == self.players[self.current_player].get_color() and piece.get_piece_name() == 'K':
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
            
    def simulate(self, move):
        new_board = Board(14, self.players, self.piece_locations.copy(), self.current_player)
        #not sure if doing a shallow copy will cause problems later on
        new_board.make_move(move)
        new_board.switch_players()
        return new_board
        
    
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
            
    def get_legal_moves():
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
        
    def get_legal_moves(self, board, moves, position):
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
        #when the pawn moves forward 1 square
        end_position_two_squares = board.getmove(position, self.direction[0] * 2, self.direction[1] * 2)
        #when the pawn moves forward two squares (only allowed at the start position)
        end_position_diag_left = board.getmove(position, self.diag_left_direction[0],	self.diag_left_direction[1])
        #when the pawn can capture a piece diagonal to the left
        end_position_diag_right = board.getmove(position, self.diag_right_direction[0], self.diag_right_direction[1])
        #when the pawn can capture a piece diagonal to the right
        if board.is_on_board(end_position):
            if board.check_for_piece(end_position) == None: #no piece infront of pawn
                moves.append(Move(position, end_position))
                if (self.start_position == position) and \
                    board.check_for_piece(end_position_two_squares) == None:
                    #no piece in either of two squares infront of pawn
                    moves.append(Move(position, end_position_two_squares))
            if board.check_for_piece(end_position_diag_left) != None:
                if board.check_for_piece(end_position_diag_left).get_color() not in self.allied_colors:
                    #enemy piece diagonal to the left
                    moves.append(Move(position, end_position_diag_left))
            if board.check_for_piece(end_position_diag_right) != None:
                if board.check_for_piece(end_position_diag_right).get_color() not in self.allied_colors:
                    #enemy piece diagonal to the right
                    moves.append(Move(position, end_position_diag_right))
        return moves
    
    def get_score(self):
        return 1
                    
    
class Knight(Piece):
    """
    The class for the Knight piece.
    """
    def get_legal_moves(self, board, moves, position):
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
        #all possible knight moves
        for direction in directions:
            end_position = board.getmove(position, direction[0], direction[1])
            if board.is_on_board(end_position):
                if board.check_for_piece(end_position) == None: #no piece on end position
                    moves.append(Move(position, end_position))
                else:
                    if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                        #enemy piece on end position
                        moves.append(Move(position, end_position))
            
        return moves
    
    def get_score(self):
        return 3
    
class Bishop(Piece):
    """
    The class for the Bishop piece.
    """
    def get_legal_moves(self, board, moves, position):
        """
        Adds all the possible bishop moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        #all possible bishop directions
        for direction in directions:
            for tiles in range(1, 10): #maximum possible amount of diagonal squares in a row
                end_position = board.getmove(position, direction[0] * tiles, direction[1] * tiles)
                #position tiles amount diagonal of the bishop
                if board.is_on_board(end_position):
                    if board.check_for_piece(end_position) == None:
                        moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            moves.append(Move(position, end_position))
                            break #cant jump over enemy piece but can capture
                        else:
                            break #cant jump over allied piece and can't capture
                else:
                    break
                
        return moves
    
    def get_score(self):
        return 5
    
class Rook(Piece):
    """
    The class for the Rook piece.
    """
    def get_legal_moves(self, board, moves, position):
        """
        Adds all the possible rook moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        #all possible rook directions
        for direction in directions:
            for tiles in range(1, 13): #maximum possible amount of straight squares in a row
                end_position = board.getmove(position, direction[0] * tiles, direction[1] * tiles)
                #position tiles amount straight of the rook
                if board.is_on_board(end_position):
                    if board.check_for_piece(end_position) == None:
                        moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                            moves.append(Move(position, end_position))
                            break #can't jump over enemy piece but can capture
                        else:
                            break #can't jump over allied piece and can't capture
                else:
                    break
                
        return moves
    
    def get_score(self):
        return 5
    
class King(Piece):
    """
    The class for the King piece.
    """
    def get_legal_moves(self, board, moves, position):
        """
        Adds all the possible king moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        #all possible king moves
        for direction in directions:
            end_position = board.getmove(position, direction[0], direction[1])
            #end positition of a certain direction of the king
            if board.is_on_board(end_position):
                if board.check_for_piece(end_position) == None:
                    moves.append(Move(position, end_position))
                    #no pieces on position thus can move king to endposition
                else:
                    if board.check_for_piece(end_position).get_color() not in self.allied_colors:
                        #can capture enemy piece thus can move king to endposition
                        moves.append(Move(position, end_position))
        return moves
    
    def get_score(self):
        return 0
    
class Queen(Piece):
    """
    The class for the Queen piece.
    """
    def get_legal_moves(self, board, moves, position):
        """
        Adds all the possible queen moves following the rules of chess to the possible move
        list not yet including checks.
        
        Args:
            board (arr): The chess board 
            moves (arr): The array of all possible moves that the player can play
            
        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        Rook.get_legal_moves(self, board, moves, position)
        Bishop.get_legal_moves(self, board, moves, position)
        #because the queen can move in the same directions as the rook and bishop combined
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
            while(True):
                algorithm = input("Choose the algorithm to be used: \n1 = Random 2 = Alpha-Beta 3 = MonteCarlo 4 = Neural Network\n")
                if algorithm in ("1", "2", "3", "4"):
                    break
            players = [HumanPlayer("red"), RandomComputerPlayer("blue", algorithm),
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
        while(not game_finished):
            self.board.show_board()
            if isinstance(self.board.get_current_player(), RandomComputerPlayer):
                self.AI_move()
                game_finished = self.round_handler()
            elif len(selected_tiles) == 2:
                selected_tiles = self.player_move(selected_tiles)
                if len(selected_tiles) == 0:
                    game_finished = self.round_handler()
            for e in p.event.get():
                if e.type == p.QUIT:
                    game_finished = True
                elif e.type == p.MOUSEBUTTONDOWN:
                    selected_tiles = self.mouse_handler(selected_tiles)
                    
                    
    def round_handler(self):
        game_finished = False
        check = True if self.board.in_check() else False
        if len(self.board.legal_moves) == 0:
            if check == True:
                print(str(self.current_player) + " got checkmated!")
            else:
                print("A stalemate has occurred!")
            game_finished = True
        else:
            self.board.switch_players()
            self.board.legal_moves = []
        return game_finished
    
    def AI_move(self):
        self.board.make_move(self.board.get_current_player().play(self.board))
        #print("Complexity: ", self.board.get_current_player().complexity)
                
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
        col = mouse_pos[0]//self.board.sq_size
        row = mouse_pos[1]//self.board.sq_size
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
    
    