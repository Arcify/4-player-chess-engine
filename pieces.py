from helpers import Move


class Piece(object):
    """
    The interface class for different pieces. It stores the position, name, color and
    allied colors of the piece. And it provides multiple functions to interact with
    the pieces.
    """

    def __init__(self, piece_name, color, team):
        """
        Initializes a piece by setting the position, name, color and allied colors
        of the piece.

        Args:
            piece_name (str): The name of piece consisting out of a capital letter
            color (str): The color of the piece
            allied_colors (str): The colors of the current piece and the allied pieces

        Returns:
            None
        """
        self.piece_name = piece_name
        self.color = color
        self.team = team

    def __str__(self):
        """
        Returns the name of the piece displayed as the color of the piece

        Args: None

        Returns (str):
            The name of the piece displayed in the color of the piece
        """
        return " " + self.piece_name + " "

    def get_legal_moves(self):
        """
        Interface method to get all possible moves for a certain piece
        """
        pass

    def get_team(self):
        """
        Returns the allied colors of the piece

        Args: None

        Returns: allied_colors (str): The allied colors of the piece
        """
        return self.team

    def get_color(self):
        """
        Returns the color of the piece

        Args: None

        Returns: color (str): The color of the piece
        """
        return self.color

    def get_piece_name(self):
        """
        Returns the name of the piece

        Args: None

        Returns: piece_name (str): The name of the piece existing out of a capital letter
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
                 diag_right_direction, team, start_position):
        """
        Initializes the pawn.

        Args:
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
        super(Pawn, self).__init__(piece_name, color, team)
        self.direction = direction
        self.diag_left_direction = diag_left_direction
        self.diag_right_direction = diag_right_direction
        self.start_position = start_position

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible pawn moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

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
            if board.check_for_piece(end_position) is None:  # no piece infront of pawn
                if poss_positions is None or end_position in poss_positions:
                    if pin_direction is None or pin_direction == (
                            self.direction[0], self.direction[1]) or pin_direction == (
                            -self.direction[0], -self.direction[1]):
                        moves.append(Move(position, end_position))
                        if poss_positions is None or end_position in poss_positions:
                            if (self.start_position == position) and \
                                    board.check_for_piece(end_position_two_squares) is None:
                                # no piece in either of two squares in front of pawn
                                moves.append(Move(position, end_position_two_squares))
            if board.check_for_piece(end_position_diag_left) is not None:
                if board.check_for_piece(end_position_diag_left).get_color() not in self.get_team():
                    # enemy piece diagonal to the left
                    if poss_positions is None or end_position_diag_left:
                        if pin_direction is None or pin_direction == (
                                self.diag_left_direction[0], self.diag_left_direction[1]) or \
                                pin_direction == (-self.diag_left_direction[0], -self.diag_left_direction[1]):
                            moves.append(Move(position, end_position_diag_left))
            if board.check_for_piece(end_position_diag_right) is not None:
                if board.check_for_piece(end_position_diag_right).get_color() not in self.get_team():
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

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible knight moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

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
                        if board.check_for_piece(end_position).get_color() not in self.get_team():
                            # enemy piece on end position
                            moves.append(Move(position, end_position))

        return moves

    def get_score(self):
        return 3


class Bishop(Piece):
    """
    The class for the Bishop piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible bishop moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

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
                    if board.check_for_piece(end_position) is None:
                        if poss_positions is None or end_position in poss_positions:
                            if pin_direction is None or direction == pin_direction or (
                                    -direction[0], -direction[1]) == pin_direction:
                                moves.append(Move(position, end_position))
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.get_team():
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

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible rook moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

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
                        if board.check_for_piece(end_position).get_color() not in self.get_team():
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


class Queen(Piece):
    """
    The class for the Queen piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible queen moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        Rook.get_legal_moves(self, board, moves, position, poss_positions, pin_info)
        Bishop.get_legal_moves(self, board, moves, position, poss_positions, pin_info)
        # because the queen can move in the same directions as the rook and bishop combined
        return moves

    def get_score(self):
        return 9


class King(Piece):
    """
    The class for the King piece.
    """

    def get_legal_moves(self, board, moves, position, poss_positions=None, pin_info=None):
        """
        Adds all the possible king moves following the rules of chess to the possible move
        list not yet including checks.

        Args:
            board (arr): The chess board
            moves (arr): The array of all possible moves that the player can play
            position (Pos): the position of the piece
            poss_positions (arr): the legal positions, or None if all positions are allowed
            pin_info (dict): the dictionary with pieces that are pinned

        Returns:
            moves (arr): The array of all possible moves that the player can play
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        # all possible king moves
        for direction in directions:
            end_position = board.getmove(position, direction[0], direction[1])
            # end position of a certain direction of the king
            if board.is_on_board(end_position):
                in_check, pin_info, check_info = board.simulate(Move(position, end_position), switch=False).check_info()
                if not in_check:
                    if board.check_for_piece(end_position) is None:
                        moves.append(Move(position, end_position))
                        # no pieces on position thus can move king to end position
                    else:
                        if board.check_for_piece(end_position).get_color() not in self.get_team():
                            # can capture enemy piece thus can move king to end position
                            moves.append(Move(position, end_position))
        return moves

    def get_score(self):
        return 0
