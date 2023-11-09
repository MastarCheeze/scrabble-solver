from __future__ import annotations

from typing import Callable, Iterator

import numpy as np
import numpy.typing as npt
from colorama import Back  # TODO remove colorama dependency

import rules as rules
from primitives import Move, PositionUtils, Position


class Board:
    """A scrabble board.

    Each tile in the board is represented by a single-character string
    * Uppercase chars represent a tile with that letter.
    * Lowercase chars represent a blank used as a tile with that letter.
    * " " represent no tiles have been placed on the square.

    Attributes
    ----------
    board
    board_string : str
        A string representing the structure of the board, used by :ref:`display` to interpolating tiles into the string.
    DL_COLOR : str
        The escape code for the colour of the double letter tile, used by :ref:`display`.
    TL_COLOR : str
        The escape code for the colour of the triple letter tile, used by :ref:`display`.
    DW_COLOR : str
        The escape code for the colour of the double word tile, used by :ref:`display`.
    TW_COLOR : str
        The escape code for the colour of the triple word tile, used by :ref:`display`.
    """

    board_string: str
    DL_COLOR = Back.CYAN
    TL_COLOR = Back.BLUE
    DW_COLOR = Back.YELLOW
    TW_COLOR = Back.RED

    def __init__(self, board: npt.NDArray[np.unicode_] | None = None) -> None:
        """Initialises an empty board.

        Parameters
        ----------
        board : ndarray, optional
            15x15 2D list of tiles to initialise the board with.
        """
        if board is None:
            self._board = np.full((15, 15), " ", dtype=object)
        else:
            self._board = board

    @property
    def board(self) -> npt.NDArray[np.unicode_]:
        """Returns the board.

        Returns
        -------
        ndarray
            15x15 2D list of tiles.
        """
        return self._board

    def get_square(self, pos: Position) -> str:
        """Gets the tile placed at the given square position.

        Parameters
        ----------
        pos : position
            Position of the square to target.

        Returns
        -------
        str
            A tile.
        """
        return self._board[pos]

    def set_square(self, pos: Position, tile: str) -> None:
        """Sets the tile placed at a given square position.

        Parameters
        ----------
        pos : position
            Position of the square to target.
        tile : str
            Tile to place at position.
        """
        self._board[pos] = tile

    def make_move(self, move: Move):
        """Make a move on the board.

        Moves should not be made before calling :ref:`get_words_formed` or else the mode made will be removed.

        Parameters
        ----------
        move : Move
            Move to make.
        """
        for tile, pos in move.tiles:
            self.set_square(pos, tile)

    def unmake_move(self, move: Move) -> None:
        """Removes a move from the board.

        Parameters
        ----------
        move : Move
            Move to remove.
        """
        for _, pos in move.tiles:
            self.set_square(pos, " ")

    def get_words_formed(self, move: Move) -> Iterator[Move]:
        """Returns all words formed by a single move.

        Moves should be made with :ref:`make_move` only after calling this function or else the mode made will be
        removed.

        Args:
            move (Move): All tiles and their positions.

        Yields:
            Move: All tiles of the word formed and their positions (includes the original word).
        """

        if len(move) <= 0:
            return

        def stop_condition(curr_square: str, curr_pos: Position):
            return curr_square == " " and curr_pos not in move.all_positions

        self.make_move(move)

        # find the original word
        across = move.across
        if across:
            base_word = Move(
                *self.traverse_axis_until_condition(move.tiles[0][1], (0, 1), stop_condition)
            )  # search for base word horizontally
        else:
            base_word = Move(
                *self.traverse_axis_until_condition(move.tiles[0][1], (1, 0), stop_condition)
            )  # search for base word vertically
        yield base_word

        for _, pos in move.tiles:
            if across:
                tiles = list(
                    self.traverse_axis_until_condition(pos, (1, 0), stop_condition)
                )  # search for word vertically
            else:
                tiles = list(
                    self.traverse_axis_until_condition(pos, (0, 1), stop_condition)
                )  # search for word horizontally

            # words are at least 2 letters long
            if len(tiles) > 1:
                yield Move(*tiles)

        self.unmake_move(move)

    def calc_score(self, move: Move) -> int:
        """Calculates the score for a move.

        Parameters
        ----------
        move : Move
            All tiles and their positions.

        Returns
        -------
        int
            The total score of the move.
        """
        total_score = 0

        # calculate score of each word formed
        for word in self.get_words_formed(move):
            score = 0
            word_multiplier = 1

            # loop through each letter
            for tile, pos in word.tiles:
                # letter score and letter bonus
                letter_multiplier = 1
                if pos in move.all_positions:  # make sure current tile newly-placed
                    if pos in rules.DL:
                        letter_multiplier = 2
                    elif pos in rules.TL:
                        letter_multiplier = 3
                score += rules.TILE_VALUE.get(tile, 0) * letter_multiplier

                # word bonus
                if pos in move.all_positions:  # make sure current tile newly-placed
                    if pos in rules.DW:
                        word_multiplier *= 2
                    elif pos in rules.TW:
                        word_multiplier *= 3

            score *= word_multiplier
            total_score += score

        # 7-letter bonus
        if len(move.tiles) == 7:
            total_score += 50

        return total_score

    def clear(self) -> None:
        """Clears the board of all tiles."""
        self._board = np.full((15, 15), " ", dtype=object)

    def copy(self) -> Board:
        """Returns a copy of the board.

        Returns
        -------
        Board
            A copy of the board.
        """
        return Board(np.copy(self._board))

    def transpose(self) -> Board:
        """Returns a copy of the board transposed.

        Returns
        -------
        Board
            A copy of the board with all the coordinates transposed.
        """
        return Board(np.transpose(self._board))

    def traverse_until_condition(
        self,
        start: Position,
        direction: Position,
        stop_condition: Callable[[str, Position], bool],
    ) -> Iterator[tuple[str, Position]]:
        """Traverses the board in the given direction.

        Iterates through squares on the board by incrementing its position by the direction, until it is out of bounds
        or a condition is fufilled.

        Parameters
        ----------
        start : position
            Starting position of the traversal.
        direction : position
            Direction of the traversal.
        stop_condition : Callable[[str, position], bool]
            Stop condition. Takes in the current tile and position. If the return value is true, the traversal is
            terminated.

        Yields
        ------
        str
            Traversed tile.
        position
            Position of the traversed tile.
        """
        current_pos = start
        while True:
            # stop traversal if out of bounds
            current_pos = PositionUtils.add_pos(current_pos, direction)
            if PositionUtils.out_of_bounds(current_pos):
                break

            # stop traversal if condition is satisfied
            current_square = self.get_square(current_pos)
            if stop_condition(current_square, current_pos):
                break

            yield current_square, current_pos

    def traverse_axis_until_condition(
        self,
        pos: Position,
        axis: Position,
        stop_condition: Callable[[str, Position], bool],
    ) -> Iterator[tuple[str, Position]]:
        """Traverses the board bidirectionally in the given direction.

        Iterates through squares on the board by first decrementing its position by the direction until it is out of
        bounds or a condition is fufilled, then incrementing.

        Parameters
        ----------
        pos : position
            Starting position of the traversal.
        axis : position
            Direction of the traversal. (1, 0) is a row traversal, (0, 1) is a column traversal.
        stop_condition : Callable[[str, position], bool]
            Stop condition. Takes in the current tile and position. If the return value is true, the traversal of one
            direction is terminated.

        Yields
        ------
        str
            Traversed tile.
        position
            Position of the traversed tile.

        Notes
        -----
        The yield value includes the starting tile and position of the traversal.
        """
        # front part
        for item in list(self.traverse_until_condition(pos, (-axis[0], -axis[1]), stop_condition))[::-1]:
            yield item
        yield self.get_square(pos), pos  # middle letter
        yield from self.traverse_until_condition(pos, axis, stop_condition)  # end part

    def traverse_axis_until_empty(
        self,
        pos: Position,
        axis: Position,
    ) -> Iterator[tuple[str, Position]]:
        """Traverses the board bidirectionally in the given direction until a blank is reached on both ends.

        Iterates through squares on the board by first decrementing its position by the direction until it is out of
        bounds or a blank square is encountered, then incrementing.

        Parameters
        ----------
        pos : position
            Starting position of the traversal.
        axis : position
            Direction of the traversal. (1, 0) is a row traversal, (0, 1) is a column traversal.

        Yields
        ------
        str
            Traversed tile.
        position
            Position of the traversed tile.

        Notes
        -----
        The yield value includes the starting tile and position of the traversal.
        """
        yield from self.traverse_axis_until_condition(
            pos,
            axis,
            lambda tile, _: tile == " ",
        )

    def display(self, *args: tuple[str, Position]):
        """Print a text-based representation of the board.

        Parameters
        ----------
        *args : tuple[str, position]
            Character and its position to be added to the board display.
        """
        contents = self._board.flatten()

        for char, pos in args:
            contents[PositionUtils.flat_pos(pos)] = char

        print(board_string.format(*contents))


# build board display debug string
SQUARE_STRING = f"{{}} {{{{}}}} {Back.RESET} "

board_string = ""
board_string += "   " + "  ".join(str(i).rjust(2) for i in range(15)) + "\n"
for rowIdx in range(15):
    board_string += str(rowIdx).rjust(2) + " "
    board_string += SQUARE_STRING * 15
    board_string += "\n\n"
board_string = board_string.rstrip()

# insert color into board display string
colors = [Back.LIGHTBLACK_EX for _ in range(15 * 15)]
for row, col in rules.DL:
    colors[PositionUtils.flat_pos((row, col))] = Board.DL_COLOR
for row, col in rules.TL:
    colors[PositionUtils.flat_pos((row, col))] = Board.TL_COLOR
for row, col in rules.DW:
    colors[PositionUtils.flat_pos((row, col))] = Board.DW_COLOR
for row, col in rules.TW:
    colors[PositionUtils.flat_pos((row, col))] = Board.TW_COLOR
board_string = board_string.format(*colors)

Board.board_string = board_string

if __name__ == "__main__":
    b = Board()
    move = Move.anchored_to_moves("banana", (7, 7), 0)
    print(b.calc_score(move))
    b.make_move(move)
    b.display()
