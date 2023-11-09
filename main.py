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

        # redraw
        draw_board(screen, solver)
        if arrow_pos is not None:
            draw_arrow(screen, arrow_pos, arrow_across)


def handle_board_keyboard_input(event: pygame.event.Event):
    global arrow_pos

    if arrow_pos is None:
        return

    direction = (0, 1) if arrow_across else (1, 0)
    letter = event.unicode.lower()
    if letter in "abcdefghijklmnopqrstuvwxyz" and not PositionUtils.out_of_bounds(arrow_pos):
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
    if letter in "abcdefghijklmnopqrstuvwxyz":
        solver.rack.append(letter.upper())
    elif letter == " ":
        if solver.rack.count(" ") < 2:
            solver.rack.append(" ")


# board setup
solver = Solver()
solver.board.make_move(Move.anchored_to_moves("HOLIDAY", (7, 3), 0, True))
solver.board.make_move(Move.anchored_to_moves("BANDANA", (4, 7), 0, False))
solver.board.make_move(Move.anchored_to_moves("GONDOLA", (9, 5), 0, True))
solver.board.make_move(Move.anchored_to_moves("BLIGHT", (6, 5), 0, False))
solver.board.make_move(Move.anchored_to_moves("DAFFS", (8, 11), 0, False))

# pygame setup
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

running = True
focus = 1  # 0 for board, 1 for rack, 2 for toolbar
arrow_pos = None
arrow_across = True
draw_board(screen, solver)
while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if BOARD_RECT.collidepoint(pos):
                focus = 0
                handle_board_mouse_input(pos)
            elif RACK_RECT.collidepoint(pos):
                focus = 1
            else:
                focus = 2

        elif event.type == pygame.KEYDOWN:
            if focus == 0:
                handle_board_keyboard_input(event)
                draw_board(screen, solver)
                if arrow_pos is not None:
                    draw_arrow(screen, arrow_pos, arrow_across)
            elif focus == 1:
                handle_rack_keyboard_input(event)
                draw_rack(screen, solver)

    # render

    # update
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
