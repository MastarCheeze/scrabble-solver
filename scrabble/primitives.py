from __future__ import annotations
from dataclasses import dataclass

Position = tuple[int, int]


class PositionUtils:
    """Utility class for positio helper methods."""

    @staticmethod
    def flat_pos(pos: Position):
        """
        Returns the 1D flat position of row and column.
        @param pos: Position.
        @return: Flat position.
        """
        return pos[0] * 15 + pos[1]

    @staticmethod
    def out_of_bounds(pos: Position) -> bool:
        """
        Returns True if position is out of bounds.
        @param pos: Position.
        @return: Bool of whether it is out of bounds.
        """
        if pos[0] < 0 or pos[0] > 14 or pos[1] < 0 or pos[1] > 14:
            return True
        return False

    @staticmethod
    def transpose(pos: Position) -> Position:
        """
        Returns the position transposed.
        @param pos: Position.
        @return: Transposed position.
        """
        return pos[::-1]


@dataclass
class Move:
    """Representation of a collection of tiles placed in a single line."""

    tiles: list[tuple[str, Position]]

    def __init__(self, *tiles: tuple[str, Position]) -> None:
        """
        Initialises a move with the given tiles and positions.
        @param tiles: List of tiles and their positions on the board.
        """

        tiles = [(tile[0].upper(), tile[1]) for tile in tiles]
        self.tiles = sorted(tiles, key=lambda tile: tile[1])

    @property
    def across(self) -> bool:
        """
        Returns whether the move made is across or down.
        @return: True if across, False if down. True if only one tile is placed or the move is a pass.
        """
        return len(self.tiles) <= 1 or self.tiles[0][1][0] == self.tiles[1][1][0]

    @property
    def all_positions(self) -> list[Position]:
        """
        All positions occupied by the tiles.
        @return: List of positions.
        """
        return [pos for _, pos in self.tiles]

    def transpose(self) -> Move:
        """
        Returns a copy of the move with all tile positions transposed.
        @return: Transposed move.
        """
        tiles_transposed: list[tuple[str, Position]] = []
        for tile, pos in self.tiles:
            tiles_transposed.append((tile, pos))

        return Move(*tiles_transposed)

    def get_tile_by_pos(self, pos: Position) -> str:
        """
        Get the letter of a tile at a given position.
        @param pos: Position.
        @return: Tile letter.
        @raise: KeyError: If the no tiles are found at position.
        """
        for tile in self.tiles:
            if tile[0] == pos[0] and tile[1] == pos[1]:
                return tile[2]
        raise KeyError(f"There is no tile at ({pos[0]}, {pos[1]})")

    @staticmethod
    def anchored_to_moves(
        word: str,
        anchor_pos: Position,
        anchor_letter_index: int,
        across: bool = False,
    ) -> Move:
        """
        Creates a new Move object with the full word and anchor position.
        @param word: The full word formed by the tiles.
        @param anchor_pos: The position of the anchor tile.
        @param anchor_letter_index: The index of the anchor tile in the word string.
        @param across: Whether the word oriented horizontally..
        @return: Move created.
        """
        tiles: list[tuple[str, Position]] = []
        for i, tile in enumerate(word):
            if across:
                pos = (anchor_pos[0], anchor_pos[1] - anchor_letter_index + i)
            else:
                pos = (anchor_pos[0] - anchor_letter_index + i, anchor_pos[1])
            tiles.append((tile, pos))

        return Move(*tiles)

    def __add__(self, __value: tuple[str, Position]) -> Move:
        return Move(*(self.tiles + [__value]))

    def __sub__(self, __value: tuple[str, Position]) -> Move:
        return Move(*set(self.tiles) - {__value})

    def __len__(self) -> int:
        return len(self.tiles)

    def __hash__(self) -> int:
        return hash(tuple(self.tiles))
