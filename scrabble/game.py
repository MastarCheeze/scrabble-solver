from scrabble import rules
from scrabble.board import Board
from scrabble.primitives import Move


class PartialGame:
    """Representation of a scrabble game from the partial viewpoint of one player"""

    def __init__(self, total_players: int = 2) -> None:
        self.board = Board()
        self.rack: list[str] = []
        self.pool = rules.TILE_POOL[:]

        self.total_players = total_players
        self.current_player = 0
        self.history: list[Move] = []

    def make_move(self, move: Move) -> None:
        """
        Makes a move on the board and updates the pool and current player
        :param move: move to make
        :return:
        """
        self.history.append(move)
        self.board.make_move(move)
        for tile, _ in move.tiles:
            self.pool.remove(tile)
        self.current_player = (self.current_player + 1) % self.total_players

    def undo_last_move(self) -> None:
        """
        Undoes the last move from the board and updates the pool and current player
        :return:
        """
        move = self.history.pop()
        self.board.unmake_move(move)
        for tile, _ in move.tiles:
            self.pool.append(tile)
        self.current_player = (self.current_player - 1) % self.total_players
