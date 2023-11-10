import pygame
from pygame import Rect

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
TOOLBAR_H = 30
TOOLBAR_BG_COLOR = "#06080a"
TOOLBAR_ICON_PADDING = 6
TOOLBAR_ICON_SIZE = TOOLBAR_H - TOOLBAR_ICON_PADDING * 2

UNDO_IMG = pygame.transform.scale(pygame.image.load("assets/undo.png"), (TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
REDO_IMG = pygame.transform.scale(pygame.image.load("assets/redo.png"), (TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
CLEAR_EDITS_IMG = pygame.transform.scale(
    pygame.image.load("assets/clear_edits.png"), (TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE)
)
CLEAR_ALL_IMG = pygame.transform.scale(
    pygame.image.load("assets/clear_all.png"), (TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE)
)
CALC_MOVE_IMG = pygame.transform.scale(
    pygame.image.load("assets/calc_move.png"), (TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE)
)
TOOLBAR_ICON_ORDER = [UNDO_IMG, REDO_IMG, CLEAR_EDITS_IMG, CLEAR_ALL_IMG]

### Status bar ###
STATUS_BAR_H = 20
STATUS_BAR_BG_COLOR = "#1f2933"
STATUS_BAR_FONT = pygame.font.Font("assets/Roboto-Regular.ttf", 12)
STATUS_BAR_FONT_COLOR = "#ffffff"
STATUS_BAR_TEXT_PADDING_X = 8
STATUS_BAR_TEXT_PADDING_Y = 2

### Dependent dimensions ###
WINDOW_SIZE = (BOARD_SIZE, TOOLBAR_H + BOARD_SIZE + RACK_H + STATUS_BAR_H)
SCREEN = pygame.display.set_mode(WINDOW_SIZE)
BOARD_RECT = Rect(0, TOOLBAR_H, BOARD_SIZE, BOARD_SIZE)
RACK_RECT = Rect(0, TOOLBAR_H + BOARD_SIZE, BOARD_SIZE, RACK_H)
RACK_TILES_Y = TOOLBAR_H + BOARD_SIZE + (RACK_H - SQUARE_SIZE) // 2
TOOLBAR_RECT = Rect(0, 0, BOARD_SIZE, TOOLBAR_H)
STATUS_BAR_RECT = Rect(0, TOOLBAR_H + BOARD_SIZE + RACK_H, BOARD_SIZE, STATUS_BAR_H)
UNDO_RECT = Rect(TOOLBAR_H * TOOLBAR_ICON_ORDER.index(UNDO_IMG), 0, TOOLBAR_H, TOOLBAR_H)
REDO_RECT = Rect(TOOLBAR_H * TOOLBAR_ICON_ORDER.index(REDO_IMG), 0, TOOLBAR_H, TOOLBAR_H)
CLEAR_EDITS_RECT = Rect(TOOLBAR_H * TOOLBAR_ICON_ORDER.index(CLEAR_EDITS_IMG), 0, TOOLBAR_H, TOOLBAR_H)
CLEAR_ALL_RECT = Rect(TOOLBAR_H * TOOLBAR_ICON_ORDER.index(CLEAR_ALL_IMG), 0, TOOLBAR_H, TOOLBAR_H)
CALC_MOVE_RECT = Rect(BOARD_SIZE - TOOLBAR_H, 0, TOOLBAR_H, TOOLBAR_H)


def draw_board(solver: Solver):
    pygame.draw.rect(SCREEN, BORDER_COLOR, BOARD_RECT)

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
                draw_square(square_pos, square_color, (row, col) == (7, 7))

            # draw tiles
            else:
                if square_pos in solver.last_move.all_positions:
                    palette = RECENT_TILE_PALETTE
                elif square_pos in solver.edits.all_positions:
                    palette = EDIT_TILE_PALETTE
                    tile = solver.edits.get_tile(square_pos)
                else:
                    palette = EXISTING_TILE_PALETTE
                draw_tile(square_pos, tile, palette)


def draw_square(board_pos: Position, color: str, star: bool = False):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    # draw square
    pygame.draw.rect(
        SCREEN,
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
        SCREEN.blit(STAR_IMG, img_pos)


def draw_tile(board_pos: Position, letter: str, palette: dict[str, str]):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    pygame.draw.rect(
        SCREEN,
        palette["tile"],
        Rect(x, y, SQUARE_SIZE, SQUARE_SIZE),
        border_radius=TILE_ROUNDED_RADIUS,
    )

    # not a blank tile
    if letter.isupper():
        # draw letter
        text = TILE_FONT.render(letter, True, palette["font"])
        text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        SCREEN.blit(text, text_pos)

        # draw score
        text = SCORE_FONT.render(str(rules.TILE_VALUE[letter]), True, palette["font"])
        text_pos = text.get_rect(bottomright=(x + SQUARE_SIZE - SCORE_PADDING[0], y + SQUARE_SIZE - SCORE_PADDING[0]))
        SCREEN.blit(text, text_pos)

    # blank tile
    else:
        # draw circle
        pygame.draw.circle(
            SCREEN,
            palette["blank_circle"],
            (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2),
            BLANK_CIRCLE_RADIUS,
        )

        # draw tilted text
        text = TILE_FONT.render(letter.upper(), True, palette["blank_font"])
        text = pygame.transform.rotozoom(text, BLANK_LETTER_TILT, 1)
        text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        SCREEN.blit(text, text_pos)


def draw_arrow(board_pos: Position, across: bool):
    x, y = pos_to_coords(board_pos)
    y += TOOLBAR_H

    pygame.draw.rect(
        SCREEN,
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
    SCREEN.blit(img, img_pos)


def draw_rack(solver: Solver):
    pygame.draw.rect(SCREEN, RACK_BG_COLOR, RACK_RECT)

    x_offset = (BOARD_SIZE - (len(solver.rack) * (SQUARE_SIZE + RACK_TILES_PADDING) - RACK_TILES_PADDING)) // 2

    for i, tile in enumerate(solver.rack):
        draw_rack_tile(x_offset + i * (SQUARE_SIZE + RACK_TILES_PADDING), tile)


def draw_rack_tile(x: int, letter: str):
    pygame.draw.rect(
        SCREEN,
        EXISTING_TILE_PALETTE["tile"],
        Rect(x, RACK_TILES_Y, SQUARE_SIZE, SQUARE_SIZE),
        border_radius=TILE_ROUNDED_RADIUS,
    )

    # draw letter
    text = TILE_FONT.render(letter, True, EXISTING_TILE_PALETTE["font"])
    text_pos = text.get_rect(center=(x + SQUARE_SIZE // 2, RACK_TILES_Y + SQUARE_SIZE // 2))
    SCREEN.blit(text, text_pos)

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
        SCREEN.blit(text, text_pos)


def draw_toolbar():
    pygame.draw.rect(SCREEN, TOOLBAR_BG_COLOR, TOOLBAR_RECT)

    # undo button
    img_pos = Rect(
        UNDO_RECT.x + TOOLBAR_ICON_PADDING,
        UNDO_RECT.y + TOOLBAR_ICON_PADDING,
        TOOLBAR_ICON_SIZE,
        TOOLBAR_ICON_SIZE,
    )
    SCREEN.blit(UNDO_IMG, img_pos)

    # redo button
    img_pos = Rect(
        REDO_RECT.x + TOOLBAR_ICON_PADDING,
        REDO_RECT.y + TOOLBAR_ICON_PADDING,
        TOOLBAR_ICON_SIZE,
        TOOLBAR_ICON_SIZE,
    )
    SCREEN.blit(REDO_IMG, img_pos)

    # clear edits button
    img_pos = Rect(
        CLEAR_EDITS_RECT.x + TOOLBAR_ICON_PADDING,
        CLEAR_EDITS_RECT.y + TOOLBAR_ICON_PADDING,
        TOOLBAR_ICON_SIZE,
        TOOLBAR_ICON_SIZE,
    )
    SCREEN.blit(CLEAR_EDITS_IMG, img_pos)

    # clear all button
    img_pos = Rect(
        CLEAR_ALL_RECT.x + TOOLBAR_ICON_PADDING,
        CLEAR_ALL_RECT.y + TOOLBAR_ICON_PADDING,
        TOOLBAR_ICON_SIZE,
        TOOLBAR_ICON_SIZE,
    )
    SCREEN.blit(CLEAR_ALL_IMG, img_pos)

    # calc move button
    img_pos = Rect(
        CALC_MOVE_RECT.x + TOOLBAR_ICON_PADDING,
        CALC_MOVE_RECT.y + TOOLBAR_ICON_PADDING,
        TOOLBAR_ICON_SIZE,
        TOOLBAR_ICON_SIZE,
    )
    SCREEN.blit(CALC_MOVE_IMG, img_pos)


def draw_status_bar(solver: Solver):
    pygame.draw.rect(SCREEN, STATUS_BAR_BG_COLOR, STATUS_BAR_RECT)

    status_text = STATUS_BAR_FONT.render(solver.status_text, True, STATUS_BAR_FONT_COLOR)
    text_pos = status_text.get_rect(
        topleft=(
            STATUS_BAR_RECT.x + STATUS_BAR_TEXT_PADDING_X,
            STATUS_BAR_RECT.y + STATUS_BAR_TEXT_PADDING_Y,
        )
    )
    SCREEN.blit(status_text, text_pos)


def pos_to_coords(pos: Position) -> Position:
    return pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE


def coords_to_pos(coords: Position) -> Position:
    return coords[1] // SQUARE_SIZE, coords[0] // SQUARE_SIZE
