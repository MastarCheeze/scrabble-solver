from typing import Iterator

import numpy as np
import numpy.typing as npt
from scipy.signal import convolve2d

from scrabble.board import Board
from scrabble.dictionary import Node, Tree
from scrabble.primitives import Move, Position, PositionUtils


class MoveGenerator:
    """Class responsible for generating all possible moves on the board."""

    CROSS_CHECK_KERNEL = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 1, 0],
    ]

    ANCHOR_KERNEL = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]

    def __init__(self, board: Board, dictionary: Tree):
        """Initialises the MoveGenerator

        Parameters
        ----------
        board : Board
            Board to be used for move generation.
        dictionary : Tree
            Dictionary tree of all valid words.
        """
        self._board = board
        self._dictionary = dictionary

    def _calc_cross_check(self, board: Board) -> npt.NDArray[np.unicode_]:
        """Calculate all tiles that can be placed on each square of the board that forms a valid word vertically when
        placed. Only generates vertical cross-checks.

        Parameters
        ----------
        board : Board
            Board to be used for cross-check set generation.

        Returns
        -------
        ndarray
            2D array of strings of all valid tiles that can be placed on each square.
        """
        cross_check = np.full((15, 15), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", dtype="<U26")

        # calculate number of neighbouring placed tiles each empty square has
        convolved = convolve2d(board.board != " ", self.CROSS_CHECK_KERNEL, mode="same")
        convolved *= board.board == " "
        for pos in zip(*np.where(convolved >= 1)):
            cross_check[pos] = ""

            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                board.set_square(pos, letter)
                word, _ = zip(*board.traverse_axis_until_empty(pos, (1, 0)))
                word = "".join(word)
                board.set_square(pos, " ")

                if len(word) > 1:
                    if self._dictionary.lookup(word):
                        cross_check[pos] += letter

        return cross_check

    def _left_part(
        self,
        rack: list[str],
        partial_word: str,
        current_node: Node,
        limit: int,
    ) -> Iterator[tuple[str, Node]]:
        """Generates all possible partial left-parts of a word.

        A left-part of a move is all tiles to the left of the main anchor square. The main anchor square is the first
        anchor square that the move overlaps, meaning the left-part of a move should not overlap an anchor square.

        Parameters
        ----------
        rack : list[str]
            List of single-character strings that represent tiles that can be used. Blanks are represented by " ". This
            list will be changed during the function runtime to simulate using up tiles, but the list will return back
            to its original values when the function finishes running.
        partial_word : str
            Partially constructed word for recursive function. Should be empty string for initial call.
        current_node : Node
            Current node of the partially constructed word for recursive function. Should be root node for initial call.
        limit : int
            The maximum length of the left-part generated. Is also the maximum number of tiles that can be placed to the
            left of the main anchor square without overlapping another anchor square.

        Yields
        ------
        str
            A possible left-part.
        Node
            The node that the left-part stops at.
        """
        yield partial_word, current_node

        if limit > 0:
            for edge, node in current_node.branch_nodes.items():
                # place a legal non-blank tile
                if edge in rack:
                    rack.remove(edge)
                    yield from self._left_part(rack, partial_word + edge, node, limit - 1)
                    rack.append(edge)

                # if a blank is in the rack, force its usage
                if " " in rack:
                    rack.remove(" ")
                    yield from self._left_part(rack, partial_word + edge.lower(), node, limit - 1)
                    rack.append(" ")

    def _right_part(
        self,
        board: Board,
        rack: list[str],
        main_anchor_pos: Position,
        main_anchor_index: int,
        cross_check: npt.NDArray[np.unicode_],
        partial_word: str,
        current_node: Node,
        current_pos: Position,
        placed: Move,
    ) -> Iterator[Move]:
        """Generates all possible moves that can be formed at a position by extending a left-part. Only generates across
        moves.

        Parameters
        ----------
        board : Board
            Current board.
        rack : list[str]
            List of single-character strings that represent tiles that can be used. Blanks are represented by " ". This
            list will be changed during the function runtime to simulate using up tiles, but the list will return back
            to its original values when the function finishes running.
        main_anchor_pos : position
            The position of the main anchor square, which is the first anchor square that the move overlaps.
        main_anchor_index : int
            The index of the tile on the main anchor square in the partial word.
        cross_check : ndarray
            Cross-check set for the current board.
        partial_word : str
            Partially constructed word for recursive function. Should be the left-part for initial call.
        current_node : Node
            Current node of the partially constructed word for recursive function. Should be the node that the left-part
            stops at for initial call.
        current_pos : position
            Position of the next tile to be placed. Should be the main anchor square for initial call.
        placed : Move
            All tiles that have been currently placed. Should be all tiles of the left-part for initial call.

        Yields
        ------
        Move
            A legal move.
        """
        if PositionUtils.out_of_bounds(current_pos):
            # check if there is a previous tile placed and if it made a legal word
            if len(partial_word) != main_anchor_index and current_node.terminal:
                yield placed.copy()
            return

        current_tile = board.get_square(current_pos)
        # if the current square is empty
        if current_tile == " ":
            # check if there is a previous tile placed and if it made a legal word
            if len(partial_word) != main_anchor_index and current_node.terminal:
                yield placed.copy()

            if len(placed) >= 7:
                return

            # loop through all possible continuations from the current node
            for edge, node in current_node.branch_nodes.items():
                if edge in cross_check[current_pos]:
                    # place tile if it is legal and not a blank
                    if edge in rack:
                        rack.remove(edge)
                        placed += (edge, current_pos)  # type: ignore
                        yield from self._right_part(
                            board,
                            rack,
                            main_anchor_pos,
                            main_anchor_index,
                            cross_check,
                            partial_word + edge,
                            node,
                            (current_pos[0], current_pos[1] + 1),
                            placed,
                        )
                        rack.append(edge)
                        placed -= (edge, current_pos)  # type: ignore

                    # if a blank can be used, force its usage
                    if " " in rack:
                        rack.remove(" ")
                        lowered_edge = edge.lower()
                        placed += (lowered_edge, current_pos)  # type: ignore
                        yield from self._right_part(
                            board,
                            rack,
                            main_anchor_pos,
                            main_anchor_index,
                            cross_check,
                            partial_word + lowered_edge,
                            node,
                            (current_pos[0], current_pos[1] + 1),
                            placed,
                        )
                        rack.append(" ")
                        placed -= (lowered_edge, current_pos)  # type: ignore

        # if the current square already has a tile
        else:
            # if the tile placed has a legal continuation from the current node, continue searching
            node = current_node.get_branch(current_tile)
            if node is not None:
                yield from self._right_part(
                    board,
                    rack,
                    main_anchor_pos,
                    main_anchor_index,
                    cross_check,
                    partial_word + current_tile,
                    node,
                    (current_pos[0], current_pos[1] + 1),
                    placed,
                )

    def _calc_all_across_moves(self, board: Board, rack: list[str]) -> Iterator[Move]:
        cross_check = self._calc_cross_check(board)
        convolved = convolve2d(board.board != " ", self.ANCHOR_KERNEL, mode="same")
        convolved *= board.board == " "
        anchors = list(zip(*np.where(convolved >= 1)))

        # if first move is not yet placed, the centre is the only anchor
        if not anchors:
            anchors = [(7, 7)]

        for anchor in anchors:
            limit = len(
                list(
                    board.traverse_until_condition(
                        anchor,
                        (0, -1),
                        lambda _, pos: pos in anchors or board.get_square(pos) != " ",
                    )
                )
            )
            # if there is space for a left-part, generate it
            if limit > 0:
                for left_part, current_node in self._left_part(rack, "", self._dictionary.root_node, min(limit, 6)):
                    yield from self._right_part(
                        board,
                        rack,
                        anchor,
                        len(left_part),
                        cross_check,
                        left_part,
                        current_node,
                        anchor,
                        Move.anchored_to_moves(left_part, anchor, len(left_part)),
                    )
            # if there no space for a left-part, retrieve all tiles to the left of the main anchor square
            else:
                existing_left_part_tiles = Move(
                    *board.traverse_until_condition(anchor, (0, -1), lambda tile, _: tile == " ")
                )
                left_part = existing_left_part_tiles.get_word()
                try:
                    yield from self._right_part(
                        board,
                        rack,
                        anchor,
                        len(left_part),
                        cross_check,
                        left_part,
                        self._dictionary.get_node(left_part),
                        anchor,
                        Move(),
                    )
                except KeyError:
                    pass

    def calc_all_moves(self, rack: list[str]) -> Iterator[Move]:
        # get all legal across moves
        yield from self._calc_all_across_moves(self._board, rack)

        # get all legal down moves
        for move in self._calc_all_across_moves(self._board.transpose(), rack):
            yield move.transpose()

        # yield pass move
        yield Move()
