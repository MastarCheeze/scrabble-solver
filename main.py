import pygame

from scrabble import board
from scrabble.board import Board
from scrabble.dictionary import Node, Tree
from scrabble.movegenerator import MoveGenerator
from scrabble.primitives import Move, PositionUtils
from solver import Solver
from ui import *


def handle_board_mouse_input(pos: tuple[int, int]):
    global arrow_pos, arrow_across

    board_pos = coords_to_pos((pos[0], pos[1] - TOOLBAR_H))

    # if clicked on empty square
    if solver.board.get_square(board_pos) == " ":
        # set new arrow pos if previously not selected
        if arrow_pos != board_pos:
            arrow_pos = board_pos
            arrow_across = True
        # change arrow to down if previously across
        elif arrow_across:
            arrow_across = False
        # remove arrow if previously down
        else:
            arrow_pos = None


def handle_board_keyboard_input(event: pygame.event.Event):
    global arrow_pos

    if arrow_pos is None:
        return

    direction = (0, 1) if arrow_across else (1, 0)
    letter = event.unicode.lower()
    if letter in list("abcdefghijklmnopqrstuvwxyz") and not PositionUtils.out_of_bounds(arrow_pos):
        # remove overlapping edit tile if it exists
        try:
            solver.edits -= (solver.edits.get_tile(arrow_pos), arrow_pos)
        except KeyError:
            pass

        # place normal tile
        if not event.mod == 1:
            solver.edits += (letter.upper(), arrow_pos)
        # place tile substituted by blank
        else:
            solver.edits += (letter, arrow_pos)

        # advance arrow to next square
        while True:
            arrow_pos = (arrow_pos[0] + direction[0], arrow_pos[1] + direction[1])
            # break if out of bounds
            if PositionUtils.out_of_bounds(arrow_pos):
                break
            # break if found empty square
            if solver.board.get_square(arrow_pos) == " ":
                if arrow_pos not in solver.edits.all_positions:
                    break

    elif event.key == pygame.K_BACKSPACE:
        # advance arrow to previous square
        while True:
            arrow_pos = (arrow_pos[0] - direction[0], arrow_pos[1] - direction[1])
            # break and revert if out of bounds
            if PositionUtils.out_of_bounds(arrow_pos):
                arrow_pos = (arrow_pos[0] + direction[0], arrow_pos[1] + direction[1])
                break
            # break and delete if found edit tiles
            if arrow_pos in solver.edits.all_positions:
                tile = solver.edits.get_tile(arrow_pos)
                solver.edits -= (tile, arrow_pos)
                break
            # break if found empty square
            if solver.board.get_square(arrow_pos) == " ":
                break


def handle_rack_keyboard_input(event: pygame.event.Event):
    if event.key == pygame.K_BACKSPACE:
        if solver.rack:
            solver.rack.pop()
        return

    if len(solver.rack) >= 7:
        return

    letter = event.unicode
    if letter in list("abcdefghijklmnopqrstuvwxyz"):
        solver.rack.append(letter.upper())
    elif letter == " ":
        if solver.rack.count(" ") < 2:
            solver.rack.append(" ")


def handle_undo():
    print(solver.history)
    if solver.history:
        for _ in range(2):
            to_undo = solver.history.pop()
            solver.board.unmake_move(to_undo)
            solver.undo_history.append(to_undo)


def handle_redo():
    print(solver.undo_history)
    if solver.undo_history:
        for _ in range(2):
            to_redo = solver.undo_history.pop()
            solver.board.make_move(to_redo)
            solver.history.append(to_redo)


def handle_clear_edits():
    solver.edits = Move()


def handle_clear_all():
    solver.history.clear()
    solver.edits = Move()
    solver.board.clear()
    solver.rack.clear()
    solver.status_text = ""


def handle_calc_move():
    # make opponent move
    solver.board.make_move(solver.edits)
    solver.history.append(solver.edits)

    # make computer move
    computer_move = max(solver.move_generator.calc_all_moves(solver.rack), key=solver.board.calc_score)
    words_formed = list(solver.board.get_words_formed(computer_move))
    if words_formed:
        solver.status_text = (
            ", ".join(move.get_word() for move in words_formed) + ": " + str(solver.board.calc_score(computer_move))
        )
    else:
        solver.status_text = "PASS"
    solver.board.make_move(computer_move)
    solver.history.append(computer_move)

    # if both moves are blank, do nothing
    if len(solver.edits) == len(computer_move) == 0:
        solver.history.pop()
        solver.history.pop()
        solver.status_text = ""
        return

    solver.undo_history.clear()
    solver.rack.clear()
    solver.edits = Move()
    solver.last_move = computer_move


# setup
solver = Solver()
pygame.init()
clock = pygame.time.Clock()

running = True
focus_board = False  # True for board, False for rack
arrow_pos = None
arrow_across = True
draw_board(solver)
draw_toolbar()
draw_rack(solver)
draw_status_bar(solver)
while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            # clicked on board
            if BOARD_RECT.collidepoint(pos):
                focus_board = True
                handle_board_mouse_input(pos)
                draw_board(solver)
                if arrow_pos is not None:
                    draw_arrow(arrow_pos, arrow_across)
                    draw_rack(solver)
            # clicked on rack
            elif RACK_RECT.collidepoint(pos):
                focus_board = False
            # clicked on toolbar icon
            elif UNDO_RECT.collidepoint(pos):
                handle_undo()
                draw_board(solver)
                if arrow_pos is not None:
                    draw_arrow(arrow_pos, arrow_across)
                    draw_rack(solver)
                draw_status_bar(solver)
            elif REDO_RECT.collidepoint(pos):
                handle_redo()
                draw_board(solver)
                arrow_pos = None
                draw_status_bar(solver)
            elif CLEAR_EDITS_RECT.collidepoint(pos):
                handle_clear_edits()
                draw_board(solver)
                arrow_pos = None
            elif CLEAR_ALL_RECT.collidepoint(pos):
                handle_clear_all()
                draw_board(solver)
                if arrow_pos is not None:
                    draw_arrow(arrow_pos, arrow_across)
                draw_rack(solver)
                draw_status_bar(solver)
            elif CALC_MOVE_RECT.collidepoint(pos):
                handle_calc_move()
                draw_board(solver)
                draw_rack(solver)
                arrow_pos = None
                draw_status_bar(solver)

        elif event.type == pygame.KEYDOWN:
            # calc move if enter is pressed
            if event.key == pygame.K_RETURN:
                handle_calc_move()
                draw_board(solver)
                draw_rack(solver)
                arrow_pos = None
                draw_status_bar(solver)
            # keydown in board
            elif focus_board:
                handle_board_keyboard_input(event)
                draw_board(solver)
                if arrow_pos is not None:
                    draw_arrow(arrow_pos, arrow_across)
                    draw_rack(solver)
            # keydown in rack
            else:
                handle_rack_keyboard_input(event)
                draw_rack(solver)

    # update
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
