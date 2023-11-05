from __future__ import annotations
from dataclasses import dataclass

from scrabble.position import Position


@dataclass
class Move:
    """Representation of a collection of tiles placed in a single line"""

    tiles: list[tuple[str, Position]]

    def __init__(self, *tiles: tuple[str, Position]) -> None:
        """
        :param tiles: list of tiles and their positions on the board
        """

        tiles = [(tile[0].upper(), tile[1]) for tile in tiles]
        self.tiles = sorted(tiles, key=lambda tile: tile[1])

    @property
    def across(self):
        """Returns whether the move made is across or down.
        Always returns True if only one tile is placed or the move is a pass."""
        return len(self.tiles) <= 1 or self.tiles[0][1][0] == self.tiles[1][1][0]

    @property
    def all_positions(self) -> list[Position]:
        """All positions of the tiles on the board"""
        return [pos for _, pos in self.tiles]

    def transpose(self) -> Move:
        """Returns a copy of the move transposed"""
        tiles_transposed: list[tuple[str, Position]] = []
        for tile, pos in self.tiles:
            tiles_transposed.append((tile, pos))

        return Move(*tiles_transposed)

    def get_tile_by_pos(self, pos: Position) -> str:
        """
        Get the letter of a tile at a given position.
        :param pos: position
        :return: tile letter
        :raises KeyError: if the move doesn't contain the position
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
        down: bool = False,
    ) -> Move:
        """
        Creates a new Move object with the full word and anchor position
        :param word: the full word formed by the tiles
        :param anchor_pos: the board position of the anchor tile
        :param anchor_letter_index: the index of the anchor tile in the word string
        :param down: is the word oriented vertically
        :return: new Move object
        """
        tiles: list[tuple[str, Position]] = []
        for i, tile in enumerate(word):
            if not down:
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
