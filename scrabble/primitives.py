from __future__ import annotations
from dataclasses import dataclass

Position = tuple[int, int]


class PositionUtils:
    """Utility class for position helper methods."""

    @staticmethod
    def flat_pos(pos: Position) -> int:
        """Returns the 1D flat position of row and column.

        Parameters
        ----------
        pos : position
            Row and column.

        Returns
        -------
        int
           Flat position.
        """
        return pos[0] * 15 + pos[1]

    @staticmethod
    def out_of_bounds(pos: Position) -> bool:
        """Checks if position is out of bounds.

        Parameters
        ----------
        pos : position
            Position to check.

        Returns
        -------
        bool
            True if it is out of bounds.
        """
        if pos[0] < 0 or pos[0] > 14 or pos[1] < 0 or pos[1] > 14:
            return True
        return False

    @staticmethod
    def transpose(pos: Position) -> Position:
        """Returns the position transposed.

        Parameters
        ----------
        pos : position
            Position to transpose.

        Returns
        -------
        position
            Transposed position.
        """
        return pos[1], pos[0]

    @staticmethod
    def add_pos(pos1: Position, pos2: Position) -> Position:
        return pos1[0] + pos2[0], pos1[1] + pos2[1]


@dataclass
class Move:
    """A collection of tiles placed in a single line and their positions."""

    tiles: list[tuple[str, Position]]

    def __init__(self, *tiles: tuple[str, Position]) -> None:
        """Initialises a move with the given tiles and positions.

        Parameters
        ----------
        *args : tuple[str, position]
            Tile and its position on the board.
        """
        self.tiles = list(tiles)

    @property
    def across(self) -> bool:
        """Returns whether the move made is across or down.

        Returns
        -------
        bool
            True if across, False if down. Always True if only one tile is placed or if the move is a pass.
        """
        return len(self.tiles) <= 1 or self.tiles[0][1][0] == self.tiles[1][1][0]

    @property
    def all_positions(self) -> list[Position]:
        """All positions occupied by all the tiles.

        Returns
        -------
        list[position]
            Position of tile.
        """
        return [pos for _, pos in self.tiles]

    def transpose(self) -> Move:
        """Returns a copy of the move with all tile positions transposed.

        Returns
        -------
        Move
            Transposed move.
        """
        tiles_transposed: list[tuple[str, Position]] = []
        for tile, pos in self.tiles:
            tiles_transposed.append((tile, (pos[1], pos[0])))

        return Move(*tiles_transposed)

    def get_tile(self, pos: Position) -> str:
        """Get the letter of a tile at a given position.

        Parameters
        ----------
        pos : position
            Position of square to target.

        Returns
        -------
        str
            Tile found.

        Raises
        ------
        KeyError
            If the no tiles are found at position.
        """
        for tile in self.tiles:
            if tile[1][0] == pos[0] and tile[1][1] == pos[1]:
                return tile[0]
        raise KeyError(f"There is no tile at ({pos[0]}, {pos[1]})")

    def get_word(self) -> str:
        """Returns the word formed by the tile when all the tiles are in a single line.

        Returns
        -------
        str
            Word formed.
        """
        if self.tiles:
            self.tiles.sort(key=lambda tile: tile[1])
            return "".join(list(zip(*self.tiles))[0])
        return ""

    def copy(self) -> Move:
        """Returns a copy of the move.

        Returns
        -------
        Move
            Copy of the move.
        """
        return Move(*self.tiles)

    @staticmethod
    def anchored_to_moves(
        word: str,
        anchor_pos: Position,
        anchor_index: int,
        across: bool = True,
    ) -> Move:
        """Creates a new Move object with the full word and anchor position.

        Parameters
        ----------
        word : str
            The full word formed by the tiles.
        anchor_pos : Position
            The position of the anchor tile on the board.
        anchor_index : int
            The index of the anchor tile in the word string.
        across : bool, optional
            Whether the word oriented horizontally, by default True

        Returns
        -------
        Move
            Move created.
        """
        tiles: list[tuple[str, Position]] = []
        for i, tile in enumerate(word):
            if across:
                pos = (anchor_pos[0], anchor_pos[1] - anchor_index + i)
            else:
                pos = (anchor_pos[0] - anchor_index + i, anchor_pos[1])
            tiles.append((tile, pos))

        return Move(*tiles)

    def __add__(self, __value: tuple[str, Position]) -> Move:
        return Move(*(self.tiles + [__value]))

    def __sub__(self, __value: tuple[str, Position]) -> Move:
        return Move(*set(self.tiles) - {__value})

    def __iadd__(self, __value: tuple[str, Position]) -> Move:
        self.tiles.append(__value)
        return self

    def __isub__(self, __value: tuple[str, Position]) -> Move:
        self.tiles.remove(__value)
        return self

    def __len__(self) -> int:
        return len(self.tiles)

    def __hash__(self) -> int:
        return hash(tuple(self.tiles))
