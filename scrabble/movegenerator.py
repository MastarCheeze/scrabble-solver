import numpy as np
import numpy.typing as npt
from scipy.signal import convolve2d

from scrabble.board import Board
from scrabble.dictionary import Tree


class MoveGenerator:
    CROSS_CHECK_KERNEL = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 1, 0],
    ]

    def __init__(self, board: Board, dictionary: Tree):
        self.board = board
        self.dictionary = dictionary

    def calc_cross_checks(self) -> npt.NDArray[np.unicode_]:
        """
        For each square, calculate all letters that forms a valid word vertically when placed.
        :return: 2D array of string of all valid letters
        """
        cross_checks = np.full((15, 15), "", dtype="<U26")

        # calculate number of neighbouring placed tiles each empty square has
        convolved = convolve2d(self.board.board != " ", self.CROSS_CHECK_KERNEL, mode="same")
        convolved *= self.board.board == " "
        for pos in zip(*np.where(convolved >= 1)):
            cross_checks[pos] = ""

            for letter in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                self.board.set_square(pos, letter)
                word, _ = zip(*self.board.traverse_axis_until_empty(pos, (1, 0)))
                word = "".join(word)
                self.board.set_square(pos, " ")

                if len(word) > 1:
                    if self.dictionary.lookup(word):
                        cross_checks[pos] += letter

        return cross_checks


if __name__ == "__main__":
    from scrabble.board import Board
    from scrabble.dictionary import Node, Tree
    from primitives import Move

    b = Board()
    d = Tree.build_from_save("assets/CSW21.pickle")
    mg = MoveGenerator(b, d)

    move = Move.anchored_to_moves("b", (7, 7), 0)
    b.make_move(move)
    b.display()

    print(mg.calc_cross_checks())
