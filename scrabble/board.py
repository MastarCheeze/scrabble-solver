from __future__ import annotations

from typing import Callable, Iterator

import numpy as np
from colorama import Fore, Back  # TODO remove colorama dependency

import scrabble.rules as rules
from scrabble.move import Move
from scrabble.position import Position
import scrabble.position as position


class Board:
    """Representation of a scrabble board"""

    board_string: str
    DL_COLOR = Back.CYAN
    TL_COLOR = Back.BLUE
    DW_COLOR = Back.YELLOW
    TW_COLOR = Back.RED

    def __init__(self) -> None:
        self._board = np.full((15, 15), " ", dtype=object)

    def get_square(self, pos: Position) -> str:
        """
        Gets the tile placed at the given square position.
        :param pos: position
        :return: tile letter
        """
        return self._board[pos]

    def set_square(self, pos: Position, tile: str) -> None:
        """
        Sets the tile placed at a given square position.
        :param pos: position
        :param tile: tile letter to place
        :return:
        """
        self._board[pos] = tile

    def make_move(self, move: Move):
        """
        Make a move on the board
        :param move: move to make
        :return:
        """
        for tile, pos in move.tiles:
            self.set_square(pos, tile)

    def unmake_move(self, move: Move) -> None:
        """
        Removes a move from the board
        :param move: move to remove
        :return:
        """
        for _, pos in move.tiles:
            self.set_square(pos, " ")

    def get_words_formed(self, move: Move) -> Iterator[Move]:
        """
        Returns all connecting words formed by a move
        :param move: move to form words from
        :return: generator of moves containing the tiles of the words formed, including the original word
        """

        def stop_condition(curr_square, curr_pos):
            return curr_square == " " and curr_pos not in move.all_positions

        self.make_move(move)

        # find the original word
        across = move.across
        if across:
            base_word = Move(
                *self.traverse_axis_until_condition(
                    move.tiles[0][1], (0, 1), stop_condition
                )
            )  # search for base word horizontally
        else:
            base_word = Move(
                *self.traverse_axis_until_condition(
                    move.tiles[0][1], (1, 0), stop_condition
                )
            )  # search for base word vertically
        yield base_word

        for tile, pos in move.tiles:
            if across:
                tiles = list(
                    self.traverse_axis_until_condition(
                        pos, (1, 0), stop_condition
                    )
                )  # search for word vertically
            else:
                tiles = list(
                    self.traverse_axis_until_condition(
                        pos, (0, 1), stop_condition
                    )
                )  # search for word horizontally

            # words are at least 2 letters long
            if len(tiles) > 1:
                yield Move(*tiles)

        self.unmake_move(move)

    def calc_score(self, move: Move) -> int:
        """
        Calculates the score for a move
        :param move: move to calculate score
        :return: score
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
        """
        Clears the board of all tiles.
        :return:
        """
        self._board = np.full((15, 15), " ", dtype=object)

    def copy(self) -> Board:
        """
        Returns a copy of the board.
        :return: board copy
        """
        c = Board()
        c._board = np.copy(self._board)
        return c

    def transpose(self) -> Board:
        """
        Returns a copy of the board transposed.
        :return: transposed board copy
        """
        t = Board()
        t._board = np.transpose(self._board)
        return t

    def traverse_until_condition(
        self,
        start: Position,
        direction: Position,
        condition: Callable[[str, Position], bool],
    ) -> Iterator[tuple[str, Position]]:
        """
        Traverses the board in the given direction
        :param start: starting board position of the traversal
        :param direction: direction of the traversal
        :param condition: stop condition
        :return: generator of all tile-position tuple pairs traversed
        """
        current_pos = start
        while True:
            # stop traversal if out of bounds
            current_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if position.out_of_bounds(current_pos):
                break

            # stop traversal if condition is satisfied
            current_square = self.get_square(current_pos)
            if condition(current_square, current_pos):
                break

            yield current_square, current_pos

    def traverse_axis_until_condition(
        self,
        pos: Position,
        axis: Position,
        condition: Callable[[str, Position], bool],
    ) -> Iterator[tuple[str, Position]]:
        """
        Traverses the board bidirectionally along the row or column axis
        :param pos: starting board position of the traversal
        :param axis: (1, 0) for row traversal, (0, 1) for column traversal
        :param condition: stop condition
        :return: generator of all tile-position tuple pairs traversed
        """
        yield from self.traverse_until_condition(
            pos, (-axis[0], -axis[1]), condition
        )  # front part
        yield self.get_square(pos), pos  # middle letter
        yield from self.traverse_until_condition(
            pos, axis, condition
        )  # end part

    def traverse_axis_until_empty(
        self,
        pos: Position,
        axis: Position,
    ) -> Iterator[tuple[str, Position]]:
        """
        Traverses the board bidirectionally along the row or column aaxis until a blank square is reached
        :param pos: starting board position of the traversal
        :param axis: (1, 0) for row traversal, (0, 1) for column traversal
        :return: generator of all tile-position tuple pairs traversed
        """
        yield from self.traverse_axis_until_condition(
            pos,
            axis,
            lambda tile, _: tile == " ",
        )

    def display(self, *args: tuple[Position, str]):
        """
        Print the board
        :param args: position and value of extra characters to add to the board display
        :return:
        """
        contents = self._board.flatten()

        for pos, s in args:
            contents[position.flat_pos(pos)] = s

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
    colors[position.flat_pos((row, col))] = Board.DL_COLOR
for row, col in rules.TL:
    colors[position.flat_pos((row, col))] = Board.TL_COLOR
for row, col in rules.DW:
    colors[position.flat_pos((row, col))] = Board.DW_COLOR
for row, col in rules.TW:
    colors[position.flat_pos((row, col))] = Board.TW_COLOR
board_string = board_string.format(*colors)

Board.boardString = board_string

if __name__ == "__main__":
    b = Board()
    move = Move.anchored_to_moves("banana", (7, 7), 0)
    print(b.calc_score(move))
    b.make_move(move)
    b.display()
