import pygame as p
from helpers import Position, Move


class Board:
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
                if self.is_on_board(Position(row, column)):
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

        Returns (bool): Whether the position is located on the chess board
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
            position (Pos): the initial position
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
                    if len(check_info) == 0:
                        return None
                    elif len(check_info) == 1:
                        if self.piece_locations[check_info[0][0]].get_piece_name() == "N":
                            self.legal_moves.append(Move(pos, check_info[0][0]))
                        else:
                            poss_positions = self.block_or_capture(check_info)
                            self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos,
                                                                                         poss_positions=poss_positions)
                    elif self.piece_locations[pos].get_piece_name() == "K":
                        self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos)
                else:
                    self.legal_moves = self.piece_locations[pos].get_legal_moves(self, self.legal_moves, pos,
                                                                                 pin_info=pin_info)
        return self.legal_moves

    def block_or_capture(self, check_info):
        possible_positions = []
        for tiles in range(1, 13):
            square = Position(self.get_king_pos().get_x() + check_info[0][1][0] * tiles,
                              self.get_king_pos().get_y() + check_info[0][1][1] * tiles)
            possible_positions.append(square)
            if square == check_info[0][0]:
                return possible_positions

    def check_info(self):
        """
        returns which enemy pieces are checking the king and which friendly pieces are blocking checks (pins)

        Args: None

        Returns: (tuple): whether the king is in check, which pieces are pinned and which pieces are delivering check

        Credits: This function has been inspired from Eddie Sharicks' youtube tutorial which can be found here:
        https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_
                """
        in_check = False
        check_info = []
        pin_info = {}
        position = self.get_king_pos()
        if position is None:
            return True, pin_info, check_info
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

        Args: None

        Returns: None
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

    def simulate(self, move, switch=True):
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
            game_finished = True
        return game_finished
