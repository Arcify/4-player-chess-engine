# -*- coding: utf-8 -*-
"""
@Author: Arcify
"""
import pygame as p
from helpers import Move, Position
from board import Board
from players import RandomComputerPlayer, HumanPlayer


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
        
        Args: None
            
        Returns: None
        """
        computer = input("Would you like to play against the computer[y][n] ")
        if computer == 'y':
            while True:
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
        
        Args: None
            
        Returns: None
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
                self.board.get_moves()
                game_finished = self.board.is_game_over()
                if not game_finished:
                    self.board.legal_moves = []
                    selected_tiles = self.player_move(selected_tiles)
                    if len(selected_tiles) == 0:
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
