import pygame
from pygame import Rect, Surface

from scrabble import rules
from scrabble.board import Board
from scrabble.primitives import Position
from solver import Solver

pygame.init()

### Board ###
# dimensions
BOARD_SIZE = 600
SQUARE_SIZE = 40
BORDER_SIZE = 1

# colors
EMPTY_COLOR = "#ffffff"
DL_COLOR = "#b1e3de"
TL_COLOR = "#71bcbd"
DW_COLOR = "#d4908e"
TW_COLOR = "#8f424b"
BORDER_COLOR = "#d7c6c6"
ARROW_BG_COLOR = "#ffffff"

EXISTING_TILE_PALETTE = {
    "tile": "#dfceb9",
    "font": "#413424",
    "blank_font": "#f4ede4",
    "blank_circle": "#816a53",
}
RECENT_TILE_PALETTE = {
    "tile": "#99846b",
    "font": "#fcf1dc",
    "blank_font": "#99846b",
    "blank_circle": "#f4ede4",
}
EDIT_TILE_PALETTE = {
    "tile": "#bea68c",
    "font": "#413424",
    "blank_font": "#f4ede4",
    "blank_circle": "#5a4b3a",
}

# fonts
TILE_FONT = pygame.font.Font("assets/Roboto-Bold.ttf", 26)
BLANK_FONT = pygame.font.Font("assets/Roboto-Bold.ttf", 24)
SCORE_FONT = pygame.font.Font("assets/Roboto-Black.ttf", 10)

# images
STAR_IMG = pygame.image.load("assets/star.png")
ARROW_ACROSS_IMG = pygame.image.load("assets/arrow_across.png")
ARROW_DOWN_IMG = pygame.image.load("assets/arrow_down.png")

# other
TILE_ROUNDED_RADIUS = 6
SCORE_PADDING = (1, 1)

BLANK_CIRCLE_RADIUS = 15
BLANK_LETTER_TILT = 10

### Rack ###
RACK_H = 80
RACK_BG_COLOR = "#06080a"
RACK_TILES_PADDING = 5

### Toolbar ###
TOOLBAR_H = 50
TOOLBAR_BG_COLOR = "#ffffff"

### Dependent dimensions ###
WINDOW_SIZE = (BOARD_SIZE, TOOLBAR_H + BOARD_SIZE + RACK_H)
BOARD_RECT = Rect(0, TOOLBAR_H, BOARD_SIZE, BOARD_SIZE)
RACK_RECT = Rect(0, TOOLBAR_H + BOARD_SIZE, BOARD_SIZE, RACK_H)
TOOLBAR_RECT = Rect(0, BOARD_SIZE, BOARD_SIZE, RACK_H)
RACK_TILES_Y = TOOLBAR_H + BOARD_SIZE + (RACK_H - SQUARE_SIZE) // 2


def draw_board(surface: Surface, solver: Solver):
    pygame.draw.rect(surface, BORDER_COLOR, BOARD_RECT)

    for row in range(15):
        for col in range(15):
            square_pos = (row, col)
            tile = solver.board.get_square(square_pos)

            # draw squares
            if tile == " " and square_pos not in solver.edits.all_positions:
                if square_pos in rules.DL:
                    square_color = DL_COLOR
                elif square_pos in rules.TL:
                    square_color = TL_COLOR
                elif square_pos in rules.DW:
                    square_color = DW_COLOR
                elif square_pos in rules.TW:
                    square_color = TW_COLOR
                else:
                    square_color = EMPTY_COLOR
                draw_square(surface, square_pos, square_color, (row, col) == (7, 7))

            # draw tiles
            else:
                if square_pos in solver.last_move.all_positions:
                    palette = RECENT_TILE_PALETTE
                elif square_pos in solver.edits.all_positions:
                    palette = EDIT_TILE_PALETTE
                    tile = solver.edits.get_tile(square_pos)
                else:
                    palette = EXISTING_TILE_PALETTE
                draw_tile(surface, square_pos, tile, palette)


def draw_square(surface: Surface, board_pos: Position, color: str, star: bool = False):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    # draw square
    pygame.draw.rect(
        surface,
        color,
        Rect(
            x + BORDER_SIZE,
            y + BORDER_SIZE,
            SQUARE_SIZE - BORDER_SIZE * 2,
            SQUARE_SIZE - BORDER_SIZE * 2,
        ),
    )

    if star:
        img_pos = STAR_IMG.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        surface.blit(STAR_IMG, img_pos)


def draw_tile(surface: Surface, board_pos: Position, letter: str, palette: dict[str, str]):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    pygame.draw.rect(
        surface,
        palette["tile"],
        Rect(x, y, SQUARE_SIZE, SQUARE_SIZE),
        border_radius=TILE_ROUNDED_RADIUS,
    )

    # not a blank tile
    if letter.isupper():
        # draw letter
        text = TILE_FONT.render(letter, True, palette["font"])
        text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        surface.blit(text, text_pos)

        # draw score
        text = SCORE_FONT.render(str(rules.TILE_VALUE[letter]), True, palette["font"])
        text_pos = text.get_rect(bottomright=(x + SQUARE_SIZE - SCORE_PADDING[0], y + SQUARE_SIZE - SCORE_PADDING[0]))
        surface.blit(text, text_pos)

    # blank tile
    else:
        print(repr(letter))
        # draw circle
        pygame.draw.circle(
            surface,
            palette["blank_circle"],
            (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2),
            BLANK_CIRCLE_RADIUS,
        )

        # draw tilted text
        text = TILE_FONT.render(letter.upper(), True, palette["blank_font"])
        text = pygame.transform.rotozoom(text, BLANK_LETTER_TILT, 1)
        text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        surface.blit(text, text_pos)


def draw_arrow(surface: Surface, board_pos: Position, across: bool):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    pygame.draw.rect(
        surface,
        ARROW_BG_COLOR,
        Rect(
            x + BORDER_SIZE,
            y + BORDER_SIZE,
            SQUARE_SIZE - BORDER_SIZE * 2,
            SQUARE_SIZE - BORDER_SIZE * 2,
        ),
    )

    # draw arrow image
    if across:
        img = ARROW_ACROSS_IMG
    else:
        img = ARROW_DOWN_IMG
    img_pos = img.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
    surface.blit(img, img_pos)


def draw_rack(surface: Surface, solver: Solver):
    pygame.draw.rect(surface, RACK_BG_COLOR, RACK_RECT)

    x_offset = (BOARD_SIZE - (len(solver.rack) * (SQUARE_SIZE + RACK_TILES_PADDING) - RACK_TILES_PADDING)) // 2

    for i, tile in enumerate(solver.rack):
        draw_rack_tile(surface, x_offset + i * (SQUARE_SIZE + RACK_TILES_PADDING), tile)


def draw_rack_tile(surface: Surface, x: int, letter: str):
    pygame.draw.rect(
        surface,
        EXISTING_TILE_PALETTE["tile"],
        Rect(x, RACK_TILES_Y, SQUARE_SIZE, SQUARE_SIZE),
        border_radius=TILE_ROUNDED_RADIUS,
    )

    # draw letter
    text = TILE_FONT.render(letter, True, EXISTING_TILE_PALETTE["font"])
    text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, RACK_TILES_Y + SQUARE_SIZE // 2))
    surface.blit(text, text_pos)

    # not a blank tile
    if letter != " ":
        # draw score
        text = SCORE_FONT.render(str(rules.TILE_VALUE[letter]), True, EXISTING_TILE_PALETTE["font"])
        text_pos = text.get_rect(
            bottomright=(
                x + SQUARE_SIZE - SCORE_PADDING[0],
                RACK_TILES_Y + SQUARE_SIZE - SCORE_PADDING[0],
            )
        )
        surface.blit(text, text_pos)


def pos_to_coords(pos: Position) -> Position:
    return pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE


def coords_to_pos(coords: Position) -> Position:
    return coords[1] // SQUARE_SIZE, coords[0] // SQUARE_SIZE
