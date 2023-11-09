from scrabble import rules
from scrabble.board import Board
from scrabble.dictionary import Tree
from scrabble.movegenerator import MoveGenerator
from scrabble.primitives import Move


class Solver:
    def __init__(self) -> None:
        self.board = Board()
        self.dictionary = Tree.build_from_save("assets/CSW21.pickle")
        self.move_generator = MoveGenerator(self.board, self.dictionary)
        self.rack: list[str] = []
        self.pool = rules.TILE_POOL[:]
        self.history: list[Move] = []
        self.last_move = Move()
        self.edits = Move()
