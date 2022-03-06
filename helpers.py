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

        Args: None

        Returns: notation (str): The move written in chess notation
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

        Args: None

        Returns: end_position (Pos): The end position of the moved piece
        """
        return self.end_position

    def get_start_position(self):
        """
        Returns the start position of the move.

        Args: None

        Returns: start_position (Pos): The start position of the moved piece
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

        Args: None

        Returns:
            x (int): The x coordinate
        """
        return self.x

    def get_y(self):
        """
        Returns the y coordinate of the position

        Args: None

        Returns: y (int): The y coordinate
        """
        return self.y
