from scrabble import rules
from scrabble.board import Board
from scrabble.primitives import Move


class PartialGame:
    """Representation of a partially-observable scrabble game from the viewpoint of a single player (observer).

    Partially-observable refers to the fact that the observer does not know the contents of the racks of other players,
    therefore cannot know the full contents of the pool.

    Attributes
    ----------
    board : Board
        Representation of the scrabble board and all tiles placed.
    rack : list[str]
        The rack of the observer.
    opponents_rack : list[int]
        The number of tiles each player currently has.
    pool : list[str]
        All game tiles, minus the tiles that are already on the board and in the observer's rack.
    total_players : int
        Total number of players.
    current_player : int
        Index of the current player to play. The observer is always index 0.
    history : list[Move]
        Record of all moves made by all players, in chronological order.
    """

    def __init__(self, total_players: int = 2, current_player: int = 0) -> None:
        """Initialises a game with an empty board and a full pool.

        Parameters
        ----------
        total_players : int, optional
            Total number of players, by default 2
        current_player : int, optional
            Index of starting player. The observer is always index 0.
        """
        self.board = Board()
        self.rack: list[str] = []
        self.opponents_rack = [0] + [7 for _ in range(total_players - 1)]
        self.pool = rules.TILE_POOL[:]

        self.total_players = total_players
        self.current_player = current_player
        self.history: list[Move] = []

    def set_rack(self, rack: list[str]):
        """Sets the observer's rack.

        Parameters
        ----------
        rack : list[str]
            Observer's new rack.
        """
        if len(rack) > 7:
            raise ValueError("Size of rack cannot exceed 7.")

        self.rack = rack

    def add_to_rack(self, rack_to_add: list[str]):
        """Adds tiles to the observer's rack.

        Parameters
        ----------
        rack_to_add : list[str]
            Tiles to add to the observer's rack.
        """
        if len(self.rack) + len(rack_to_add) > 7:
            raise ValueError("Size of rack cannot exceed 7.")

        self.rack.extend(rack_to_add)

    def make_move(self, move: Move) -> None:
        """Makes a move on the board and updates the pool, observer's rack and current player.

        Parameters
        ----------
        move : Move
            Move to make.
        """
        self.history.append(move)
        self.board.make_move(move)
        for tile, _ in move.tiles:
            try:
                self.pool.remove(tile)
            except ValueError:
                raise ValueError(f"Attempt to use a '{tile}' tile when there are not enough in the pool.")
            if self.current_player == 0:
                try:
                    self.rack.remove(tile)
                except ValueError:
                    raise ValueError(
                        f"Attempt to use a '{tile}' tile when there are not enough in the observer's rack."
                    )
        self.current_player = (self.current_player + 1) % self.total_players

    def undo_last_move(self) -> None:
        """Undoes the last move from the board and updates the pool, observer's rack and current player. Does nothing if
        there are no moves to undo"""
        if self.history:
            move = self.history.pop()
            self.board.unmake_move(move)
            for tile, _ in move.tiles:
                self.pool.append(tile)
            self.current_player = (self.current_player - 1) % self.total_players
