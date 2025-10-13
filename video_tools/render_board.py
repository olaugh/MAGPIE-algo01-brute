#!/usr/bin/env python3
"""
Scrabble board renderer - generates PNG from CGP position string.

Usage:
    python3 render_board.py "cgp_string" output.png
    python3 render_board.py --file position.cgp output.png
    python3 render_board.py --theme light-theme "cgp_string" output.png
    python3 render_board.py --supersample 4 "cgp_string" output.png
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Dict

# Default theme (dark-theme)
GRAY_16_PERCENT = (41, 41, 41)      # Background
GRAY_20_PERCENT = (51, 51, 51)      # Empty squares
GRAY_40_PERCENT = (102, 102, 102)   # Grid lines
PREMIUM_RED = (100, 50, 50)         # Triple word score (TWS)
PREMIUM_PINK = (155, 80, 80)        # Double word score (DWS) and center
PREMIUM_DARKBLUE = (40, 80, 140)    # Triple letter score (TLS)
PREMIUM_LIGHTBLUE = (120, 140, 180) # Double letter score (DLS)
GOLDEN = (240, 220, 180)            # Tile background
LETTER_COLOR = (0, 0, 0)            # Black letters
DARKRED = (72, 16, 16)              # Blank tile outline

# Current theme colors (updated by load_theme)
THEME = {
    'BACKGROUND': GRAY_16_PERCENT,
    'EMPTY_SQUARE': GRAY_20_PERCENT,
    'PREMIUM_RED': PREMIUM_RED,
    'PREMIUM_PINK': PREMIUM_PINK,
    'PREMIUM_DARKBLUE': PREMIUM_DARKBLUE,
    'PREMIUM_LIGHTBLUE': PREMIUM_LIGHTBLUE,
    'TILE': GOLDEN,
    'LETTER': LETTER_COLOR,
    'BLANK_OUTLINE': DARKRED,
    'GRADIENT_EMPTY': 0.04,  # Concave gradient opacity for empty squares
    'GRADIENT_TILE': 0.18,   # Convex gradient opacity for tiles
}

# Board layout
BOARD_DIM = 15
BASE_SQUARE_SIZE = 63  # At 1x scale
BASE_BOARD_SIZE = BOARD_DIM * BASE_SQUARE_SIZE

# Tile sizing (from raylib prototype)
TILE_FRACTION = 0.88  # Increased from 0.85 to reduce grid spacing by 20%
CORNER_RADIUS_FRACTION = 0.25
GRADIENT_FRACTION = 0.98

# Text positioning
LETTER_OFFSET_UP = 0.05
BLANK_SIZE_FRACTION = 0.6667
POINT_SIZE_1_DIGIT = 0.3192  # 0.42 * 0.8 * 0.95 (20% + 5% reduction) - kept as is
POINT_SIZE_2_DIGIT = 0.2452  # 0.35 * 0.8 * 0.95 * 0.96 * 0.96 (20% + 5% + 4% + 4% reduction)

# Point value positioning (as fraction of gradient_size, then pixel adjustments)
POINT_H_OFFSET_1_DIGIT = 0.88  # Single digit horizontal base
POINT_H_OFFSET_2_DIGIT = 0.82  # Two digit horizontal base
POINT_V_OFFSET = 0.80          # Vertical base

# Pixel adjustments (at 1x scale)
POINT_ADJUST_1_DIGIT = (-2, -2)  # (x, y) adjustment for 1-digit scores
POINT_ADJUST_2_DIGIT = (1, -1)   # (x, y) adjustment for 2-digit scores

# Bonus square layout
BONUS_SQUARES = {
    'TWS': [(0,0), (0,7), (0,14), (7,0), (7,14), (14,0), (14,7), (14,14)],
    'DWS': [(1,1), (2,2), (3,3), (4,4), (1,13), (2,12), (3,11), (4,10),
            (10,4), (11,3), (12,2), (13,1), (10,10), (11,11), (12,12), (13,13)],
    'TLS': [(1,5), (1,9), (5,1), (5,5), (5,9), (5,13), (9,1), (9,5), (9,9), (9,13), (13,5), (13,9)],
    'DLS': [(0,3), (0,11), (2,6), (2,8), (3,0), (3,7), (3,14), (6,2), (6,6), (6,8), (6,12),
            (7,3), (7,11), (8,2), (8,6), (8,8), (8,12), (11,0), (11,7), (11,14), (12,6), (12,8), (14,3), (14,11)],
}

LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
    'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
}


def load_theme(theme_name: str) -> None:
    """
    Load a color theme from themes directory.

    Args:
        theme_name: Name of theme file (with or without .txt extension)
    """
    global THEME

    if not theme_name.endswith('.txt'):
        theme_name += '.txt'

    theme_dir = os.path.join(os.path.dirname(__file__), 'themes')
    theme_path = os.path.join(theme_dir, theme_name)

    if not os.path.exists(theme_path):
        print(f"Warning: Theme file not found: {theme_path}", file=sys.stderr)
        print(f"Using default theme", file=sys.stderr)
        return

    with open(theme_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Parse values - could be RGB tuple or single float
                try:
                    if ',' in value:
                        # RGB color tuple
                        rgb = tuple(int(x.strip()) for x in value.split(','))
                        if len(rgb) == 3:
                            THEME[key] = rgb
                    else:
                        # Single float value (for gradients)
                        THEME[key] = float(value.strip())
                except ValueError:
                    print(f"Warning: Invalid value for {key}: {value}", file=sys.stderr)


def parse_cgp_board(board_string: str) -> List[List[Optional[str]]]:
    """Parse CGP board string into 15x15 grid."""
    board = [[None for _ in range(15)] for _ in range(15)]
    rows = board_string.split('/')

    for row_idx, row_str in enumerate(rows):
        if row_idx >= 15:
            break

        col_idx = 0
        i = 0
        while i < len(row_str) and col_idx < 15:
            char = row_str[i]
            if char.isdigit():
                col_idx += int(char)
            elif char.isalpha():
                board[row_idx][col_idx] = char
                col_idx += 1
            i += 1

    return board


def get_bonus_color(row: int, col: int) -> Tuple[int, int, int]:
    """Get color for bonus square at position."""
    pos = (row, col)
    if pos in BONUS_SQUARES['TWS']:
        return THEME['PREMIUM_RED']
    if pos in BONUS_SQUARES['DWS'] or pos == (7, 7):  # Center is DWS color
        return THEME['PREMIUM_PINK']
    if pos in BONUS_SQUARES['TLS']:
        return THEME['PREMIUM_DARKBLUE']
    if pos in BONUS_SQUARES['DLS']:
        return THEME['PREMIUM_LIGHTBLUE']
    return THEME['EMPTY_SQUARE']


def get_bonus_label(row: int, col: int) -> Optional[str]:
    """Get label text for bonus square at position (3W, 2W, 3L, 2L)."""
    pos = (row, col)
    if pos in BONUS_SQUARES['TWS']:
        return '3W'
    if pos in BONUS_SQUARES['DWS'] or pos == (7, 7):
        return '2W'
    if pos in BONUS_SQUARES['TLS']:
        return '3L'
    if pos in BONUS_SQUARES['DLS']:
        return '2L'
    return None


def round_corners_with_paint(draw: ImageDraw.Draw, bbox: Tuple[int, int, int, int],
                            radius: int, bg_color: Tuple[int, int, int]):
    """
    Round corners by painting background color to mask the sharp corners.
    We draw a circle at each corner and paint the OUTSIDE quarter (the corner of the square).
    """
    x1, y1, x2, y2 = bbox

    # Use polygons to fill the corners more precisely
    # For each corner, create a polygon that fills the triangular space outside the rounded corner

    # Top-left corner
    # Create a circular arc from the corner
    import math
    steps = 32  # Number of points in the arc for smoothness

    # Top-left: arc from (x1, y1+radius) to (x1+radius, y1)
    points = [(x1, y1)]  # Corner point
    for i in range(steps + 1):
        angle = math.pi / 2 * i / steps  # 0 to 90 degrees
        px = x1 + radius * (1 - math.cos(angle))
        py = y1 + radius * (1 - math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=bg_color)

    # Top-right: arc from (x2-radius, y1) to (x2, y1+radius)
    points = [(x2, y1)]
    for i in range(steps + 1):
        angle = math.pi / 2 * i / steps
        px = x2 - radius * (1 - math.cos(angle))
        py = y1 + radius * (1 - math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=bg_color)

    # Bottom-left: arc from (x1+radius, y2) to (x1, y2-radius)
    points = [(x1, y2)]
    for i in range(steps + 1):
        angle = math.pi / 2 * i / steps
        px = x1 + radius * (1 - math.cos(angle))
        py = y2 - radius * (1 - math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=bg_color)

    # Bottom-right: arc from (x2, y2-radius) to (x2-radius, y2)
    points = [(x2, y2)]
    for i in range(steps + 1):
        angle = math.pi / 2 * i / steps
        px = x2 - radius * (1 - math.cos(angle))
        py = y2 - radius * (1 - math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=bg_color)


def draw_rounded_rect_mask(img: Image.Image, bbox: Tuple[int, int, int, int],
                          radius: int, fill: Tuple[int, int, int]):
    """
    Draw a hard-edged rounded rectangle using a mask.
    No anti-aliasing - we rely on 4x supersampling for smoothness.
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    # Create an L (grayscale) mask to capture rounded_rectangle output
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)

    # Draw filled rounded rectangle on mask (this will create anti-aliased edges)
    mask_draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=radius, fill=255)

    # Threshold the mask to remove anti-aliasing: convert all non-zero values to 255
    # This eliminates the gray overhang by making pixels either fully opaque or transparent
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            # Set to 255 if >= 128, else 0 (binary threshold)
            pixels[x, y] = 255 if pixels[x, y] >= 128 else 0

    # Create a solid color image
    color_img = Image.new('RGB', (width, height), fill)

    # Paste color onto main image using the thresholded mask (hard edges, no blending)
    img.paste(color_img, (x1, y1), mask)


def draw_rounded_rect(draw: ImageDraw.Draw, bbox: Tuple[int, int, int, int],
                     radius: int, fill: Optional[Tuple[int, int, int]],
                     outline: Optional[Tuple[int, int, int]] = None, width: int = 1):
    """Compatibility wrapper - not used in RGB mode."""
    # This is only kept for compatibility, actual rendering uses draw_rounded_rect_mask
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def apply_gradient(img: Image.Image, bbox: Tuple[int, int, int, int],
                   is_tile: bool = True):
    """
    Apply gradient overlay for depth effect (RGBA version).

    is_tile=True: Convex (white top → black bottom at 18% opacity) for raised tiles
    is_tile=False: Concave (black top → white bottom at 4% opacity) for inset squares
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    gradient = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(gradient)

    if is_tile:
        # Convex: white at top, black at bottom (18% opacity)
        for y in range(height):
            ratio = y / height
            r = int(255 * (1 - ratio))
            alpha = int(255 * 0.18)
            draw.line([(0, y), (width, y)], fill=(r, r, r, alpha))
    else:
        # Concave: black at top, white at bottom (4% opacity)
        for y in range(height):
            ratio = y / height
            r = int(255 * ratio)
            alpha = int(255 * 0.04)
            draw.line([(0, y), (width, y)], fill=(r, r, r, alpha))

    img.paste(gradient, (x1, y1), gradient)


def apply_gradient_rgb(img: Image.Image, bbox: Tuple[int, int, int, int],
                       is_tile: bool = True):
    """
    Apply gradient overlay for depth effect (RGB version - manual blending).

    is_tile=True: Convex (white top → black bottom) for raised tiles
    is_tile=False: Concave (black top → white bottom) for inset squares
    Opacity values come from THEME['GRADIENT_TILE'] or THEME['GRADIENT_EMPTY']
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    # Load pixel data for direct manipulation
    pixels = img.load()

    opacity = THEME['GRADIENT_TILE'] if is_tile else THEME['GRADIENT_EMPTY']

    for y in range(height):
        ratio = y / height
        if is_tile:
            # Convex: white at top, black at bottom
            gradient_value = int(255 * (1 - ratio))
        else:
            # Concave: black at top, white at bottom
            gradient_value = int(255 * ratio)

        for x in range(width):
            px = x1 + x
            py = y1 + y
            if 0 <= px < img.width and 0 <= py < img.height:
                r, g, b = pixels[px, py]
                # Manual alpha blending: result = bg * (1 - alpha) + fg * alpha
                r = int(r * (1 - opacity) + gradient_value * opacity)
                g = int(g * (1 - opacity) + gradient_value * opacity)
                b = int(b * (1 - opacity) + gradient_value * opacity)
                pixels[px, py] = (r, g, b)


def render_board(scale: int = 4, board: Optional[List[List[Optional[str]]]] = None,
                 show_labels: bool = False, premium_font: ImageFont.ImageFont = None) -> Image.Image:
    """
    Render Scrabble board and tiles at specified scale.

    Args:
        scale: Render scale multiplier (4 = 4x supersampling for antialiasing)
        board: Optional board state (used to skip drawing empty squares under tiles)
        show_labels: If True, use asymmetric margins (larger top/left for labels)

    Returns:
        PIL Image with board and tiles
    """
    square_size = BASE_SQUARE_SIZE * scale
    board_size = BASE_BOARD_SIZE * scale

    # Use asymmetric margins when labels are shown
    if show_labels:
        margin_top = 38 * scale     # 2px tighter than left
        margin_left = 40 * scale    # Keep at 40px for row labels
        margin_bottom = 13 * scale  # 2px tighter (no labels)
        margin_right = 13 * scale   # 2px tighter (no labels)
    else:
        # Symmetric margins when no labels
        margin_top = margin_left = margin_bottom = margin_right = 40 * scale

    img_width = board_size + margin_left + margin_right
    img_height = board_size + margin_top + margin_bottom

    # Create RGB image directly (no alpha channel = no anti-aliasing blending)
    img = Image.new('RGB', (img_width, img_height), THEME['BACKGROUND'])
    draw = ImageDraw.Draw(img)

    # Draw board squares with concave gradient and rounded borders (like raylib)
    tile_size = int(square_size * TILE_FRACTION)
    tile_margin = (square_size - tile_size) // 2
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            x = margin_left + col * square_size + tile_margin
            y = margin_top + row * square_size + tile_margin

            # Skip drawing colored square if there's a tile here (tile will be drawn on top)
            # BUT still draw the background shape
            if board and board[row][col]:
                # Draw background-colored square for proper masking
                draw.rectangle([x, y, x + tile_size, y + tile_size], fill=THEME['BACKGROUND'])
            else:
                # Draw colored square for empty positions
                color = get_bonus_color(row, col)
                draw.rectangle([x, y, x + tile_size, y + tile_size], fill=color)

            # Apply concave gradient to ALL squares (creates the inset effect)
            # MUST be done before rounding corners so gradient doesn't bleed into background
            grad_x = x + gradient_offset
            grad_y = y + gradient_offset
            apply_gradient_rgb(img, (grad_x, grad_y,
                               grad_x + gradient_size,
                               grad_y + gradient_size),
                          is_tile=False)

            # Round the corners by painting over them with background color
            # This MUST be last so corners are clean
            round_corners_with_paint(draw, (x, y, x + tile_size, y + tile_size),
                                    corner_radius, THEME['BACKGROUND'])

            # Draw premium square labels (3W, 2W, 3L, 2L) on empty squares
            if not (board and board[row][col]):
                bonus_label = get_bonus_label(row, col)
                if bonus_label and premium_font:
                    # Center the text in the gradient region
                    text_x = grad_x + gradient_size // 2
                    text_y = grad_y + gradient_size // 2
                    draw.text((text_x, text_y), bonus_label, fill=(255, 255, 255),
                             font=premium_font, anchor='mm')

    return img


def draw_tile(img: Image.Image, draw: ImageDraw.Draw, letter: str,
             row: int, col: int, scale: int,
             font_letter: ImageFont.ImageFont, font_value: ImageFont.ImageFont,
             margin_left: int = None, margin_top: int = None):
    """Draw a single tile on the board."""
    square_size = BASE_SQUARE_SIZE * scale
    if margin_left is None:
        margin_left = 40 * scale
    if margin_top is None:
        margin_top = 40 * scale

    # Tile sizing
    tile_size = int(square_size * TILE_FRACTION)
    tile_margin = (square_size - tile_size) // 2
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)

    # Gradient region
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    x = margin_left + col * square_size + tile_margin
    y = margin_top + row * square_size + tile_margin

    is_blank = letter.islower()
    display_letter = letter.upper()

    # Draw tile background
    draw.rectangle([x, y, x + tile_size, y + tile_size], fill=THEME['TILE'])

    # Apply convex gradient overlay (tiles are raised)
    # MUST be done before rounding corners so gradient doesn't bleed into background
    grad_x = x + gradient_offset
    grad_y = y + gradient_offset
    apply_gradient_rgb(img, (grad_x, grad_y, grad_x + gradient_size, grad_y + gradient_size),
                      is_tile=True)

    # Round the corners by painting over them with background color
    # This MUST be last so corners are clean
    round_corners_with_paint(draw, (x, y, x + tile_size, y + tile_size),
                            corner_radius, THEME['BACKGROUND'])

    # Draw semi-transparent black border around tile (1.5 pixels, 50% opacity)
    # Position slightly outward to give more space to score text
    border_width = int(1.5 * scale)
    border_inset = -1 * scale  # Negative to expand outward

    # Create semi-transparent overlay for border
    border_img = Image.new('RGBA', (tile_size + 2 * abs(border_inset), tile_size + 2 * abs(border_inset)), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    border_draw.rounded_rectangle(
        [(0, 0), (border_img.width - 1, border_img.height - 1)],
        radius=corner_radius,
        outline=(0, 0, 0, 128),  # 50% opacity
        width=border_width
    )

    # Paste border onto main image
    img.paste(border_img, (x + border_inset, y + border_inset), border_img)

    # Letter
    if is_blank:
        letter_size = int(gradient_size * BLANK_SIZE_FRACTION)
    else:
        letter_size = int(gradient_size * 0.7145)  # 0.95 * 0.9 * 0.92 * 0.96 * 0.96 * 0.985 (10% + 8% + 4% + 4% + 1.5% reduction)

    try:
        font_sized = ImageFont.truetype(font_letter.path, letter_size)
    except:
        font_sized = font_letter

    # Get text metrics for proper centering (anchor='mm' centers both horizontally and vertically)
    letter_x = grad_x + gradient_size // 2
    letter_y = grad_y + int((0.5 - LETTER_OFFSET_UP) * gradient_size)

    draw.text((letter_x, letter_y), display_letter, fill=THEME['LETTER'], font=font_sized, anchor='mm')

    # Blank outline
    if is_blank:
        blank_offset = int(gradient_size * (1 - BLANK_SIZE_FRACTION) / 2)
        blank_size = int(gradient_size * BLANK_SIZE_FRACTION)
        blank_x = grad_x + blank_offset
        blank_y = grad_y + blank_offset
        blank_radius = int(blank_size * 0.25)  # Increased from 0.15 to 0.25 for more rounding
        blank_width = 2 * scale  # 2 pixels at 1x scale
        draw_rounded_rect(draw, (blank_x, blank_y, blank_x + blank_size, blank_y + blank_size),
                         blank_radius, None, THEME['BLANK_OUTLINE'], blank_width)

    # Point value
    elif display_letter in LETTER_VALUES:
        value = str(LETTER_VALUES[display_letter])
        value_size = int(gradient_size * (POINT_SIZE_1_DIGIT if len(value) == 1 else POINT_SIZE_2_DIGIT))

        try:
            font_val_sized = ImageFont.truetype(font_value.path, value_size)
        except:
            font_val_sized = font_value

        # Use different horizontal offset for 1-digit vs 2-digit scores
        # Apply pixel adjustments from constants
        h_offset = POINT_H_OFFSET_1_DIGIT if len(value) == 1 else POINT_H_OFFSET_2_DIGIT
        val_x = grad_x + int(h_offset * gradient_size)
        val_y = grad_y + int(POINT_V_OFFSET * gradient_size)

        # Apply pixel adjustments: 1-digit: (-2, -2), 2-digit: (+1, -1)
        adjust_x, adjust_y = POINT_ADJUST_1_DIGIT if len(value) == 1 else POINT_ADJUST_2_DIGIT
        val_x += adjust_x * scale
        val_y += adjust_y * scale

        draw.text((val_x, val_y), value, fill=THEME['LETTER'], font=font_val_sized, anchor='mm')


def render_position(cgp_string: str, output_path: str, supersample: int = 1, show_labels: bool = False,
                   video_mode: bool = False, video_bg: Tuple[int, int, int] = (100, 32, 128)):
    """
    Render CGP position to PNG with antialiasing.

    Args:
        cgp_string: CGP format string
        output_path: Output PNG file path
        supersample: Render at Nx resolution then downsample (default: 1, use 4 for final quality)
        show_labels: Show column (A-O) and row (1-15) labels around the board
        video_mode: If True, render centered in 1920x1080 landscape frame
        video_bg: Background color for video mode (default: purple 100, 32, 128)
    """
    # Parse CGP
    parts = cgp_string.strip().split()
    if len(parts) < 2 or parts[0] != 'cgp':
        raise ValueError("Invalid CGP format")

    board = parse_cgp_board(parts[1])

    # Load font for premium square labels first (need before rendering board)
    import os
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        # 15% larger than 14pt = 14 * 1.15 = 16.1pt
        premium_font = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), int(16.1 * supersample))
    except:
        premium_font = ImageFont.load_default()

    # Render at high resolution (pass board and show_labels so we use correct margins)
    img = render_board(scale=supersample, board=board, show_labels=show_labels, premium_font=premium_font)
    draw = ImageDraw.Draw(img)

    # Calculate margins for tile drawing (must match render_board)
    if show_labels:
        margin_left = 40 * supersample
        margin_top = 40 * supersample
    else:
        margin_left = 40 * supersample
        margin_top = 40 * supersample

    # Load fonts (ClearSans-Bold for letters, Roboto-Bold for point values)
    import os
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')

    try:
        font_letter = ImageFont.truetype(os.path.join(font_dir, 'ClearSans-Bold.ttf'), 48 * supersample)
        font_value = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), 22 * supersample)
    except Exception as e:
        print(f"Warning: Could not load project fonts ({e}), trying system fonts", file=sys.stderr)
        try:
            font_letter = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48 * supersample)
            font_value = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22 * supersample)
        except:
            print("Warning: Using default fonts", file=sys.stderr)
            font_letter = ImageFont.load_default()
            font_value = ImageFont.load_default()

    # Draw tiles
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            if board[row][col]:
                draw_tile(img, draw, board[row][col], row, col, supersample, font_letter, font_value,
                         margin_left, margin_top)

    # Draw labels if requested
    if show_labels:
        square_size = BASE_SQUARE_SIZE * supersample
        label_offset = int(margin_top * 0.75)  # Column labels
        # Make labels darker - blend empty square color 60% with black
        empty_r, empty_g, empty_b = THEME['EMPTY_SQUARE']
        label_color = (int(empty_r * 0.6), int(empty_g * 0.6), int(empty_b * 0.6))

        # Load font for labels
        try:
            label_font = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), int(20 * supersample))
        except:
            label_font = ImageFont.load_default()

        # Column labels (A-O) at top only
        for col in range(BOARD_DIM):
            label = chr(ord('A') + col)
            x = margin_left + col * square_size + square_size // 2
            draw.text((x, label_offset), label, fill=label_color, font=label_font, anchor='mm')

        # Row labels (1-15) at left only
        # Use right-aligned anchor so two-digit numbers have same right edge as one-digit
        # Use larger offset to move them further from the board
        row_label_offset = int(margin_left * 0.9)  # Further than 0.75 for columns
        for row in range(BOARD_DIM):
            label = str(row + 1)
            y = margin_top + row * square_size + square_size // 2
            draw.text((row_label_offset, y), label, fill=label_color, font=label_font, anchor='rm')

    # Downsample for antialiasing (img is already RGB)
    # Use NEAREST or BOX to avoid creating gray halos during downsampling
    if show_labels:
        final_width = BASE_BOARD_SIZE + 40 + 13   # 40px left + 13px right
        final_height = BASE_BOARD_SIZE + 38 + 13  # 38px top + 13px bottom
    else:
        final_width = BASE_BOARD_SIZE + 80  # 40px each side
        final_height = BASE_BOARD_SIZE + 80
    final_img = img.resize((final_width, final_height), Image.BOX)

    # If video mode, compose centered in 1920x1080 frame
    if video_mode:
        video_width = 1920
        video_height = 1080
        video_frame = Image.new('RGB', (video_width, video_height), video_bg)

        # Center the board horizontally and vertically
        x_offset = (video_width - final_width) // 2
        y_offset = (video_height - final_height) // 2

        video_frame.paste(final_img, (x_offset, y_offset))
        final_img = video_frame
        print(f"Rendered {img.size[0]}×{img.size[1]}px → {final_width}×{final_height}px → {video_width}×{video_height}px (video mode, {supersample}x supersampling)")
    else:
        print(f"Rendered {img.size[0]}×{img.size[1]}px → {final_width}×{final_height}px ({supersample}x supersampling)")

    # Save
    final_img.save(output_path)
    print(f"Saved to {output_path}")


def render_debug_squares(output_path: str, supersample: int = 4):
    """
    Render individual squares at large scale for inspection.
    Creates two large squares: empty non-premium and a tile.
    """
    square_size = BASE_BOARD_SIZE * supersample  # Use full board size for one square
    margin = 40 * supersample

    img_width = square_size * 2 + 3 * margin  # Two squares side by side
    img_height = square_size + 2 * margin

    # Create RGB image (no alpha = no anti-aliasing blending)
    img = Image.new('RGB', (img_width, img_height), GRAY_16_PERCENT)
    draw = ImageDraw.Draw(img)

    # Calculate tile dimensions
    tile_size = int(square_size * TILE_FRACTION)
    tile_margin = (square_size - tile_size) // 2
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    # Square 1: Empty non-premium square
    x1 = margin + tile_margin
    y1 = margin + tile_margin
    draw_rounded_rect_mask(img, (x1, y1, x1 + tile_size, y1 + tile_size),
                          corner_radius, GRAY_20_PERCENT)

    # Apply concave gradient
    grad_x1 = x1 + gradient_offset
    grad_y1 = y1 + gradient_offset
    apply_gradient_rgb(img, (grad_x1, grad_y1,
                            grad_x1 + gradient_size,
                            grad_y1 + gradient_size),
                      is_tile=False)

    # Square 2: Tile with letter
    x2 = margin * 2 + square_size + tile_margin
    y2 = margin + tile_margin
    draw_rounded_rect_mask(img, (x2, y2, x2 + tile_size, y2 + tile_size),
                          corner_radius, GOLDEN)

    # Apply convex gradient
    grad_x2 = x2 + gradient_offset
    grad_y2 = y2 + gradient_offset
    apply_gradient_rgb(img, (grad_x2, grad_y2,
                            grad_x2 + gradient_size,
                            grad_y2 + gradient_size),
                      is_tile=True)

    # Load fonts
    import os
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')

    try:
        font_letter = ImageFont.truetype(os.path.join(font_dir, 'ClearSans-Bold.ttf'), int(gradient_size * 0.95))
        font_value = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), int(gradient_size * POINT_SIZE_1_DIGIT))
    except Exception as e:
        print(f"Warning: Could not load fonts ({e})", file=sys.stderr)
        font_letter = ImageFont.load_default()
        font_value = ImageFont.load_default()

    # Draw letter 'G' with point value
    letter_x = grad_x2 + gradient_size // 2
    letter_y = grad_y2 + int((0.5 - LETTER_OFFSET_UP) * gradient_size)
    draw.text((letter_x, letter_y), 'G', fill=LETTER_COLOR, font=font_letter, anchor='mm')

    # Point value
    val_x = grad_x2 + int(POINT_H_OFFSET * gradient_size)
    val_y = grad_y2 + int(POINT_V_OFFSET * gradient_size)
    draw.text((val_x, val_y), '2', fill=LETTER_COLOR, font=font_value, anchor='mm')

    # Downsample (img is already RGB)
    # Use BOX to avoid creating gray halos during downsampling
    final_size_w = (BASE_BOARD_SIZE * 2 + 120) // supersample * supersample
    final_size_h = (BASE_BOARD_SIZE + 80) // supersample * supersample
    final_img = img.resize((final_size_w, final_size_h), Image.BOX)

    # Save
    final_img.save(output_path)
    print(f"Debug render: {img.size[0]}×{img.size[1]}px → {final_size_w}×{final_size_h}px ({supersample}x supersampling)")
    print(f"Saved to {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 render_board.py [--theme THEME] [--supersample N] [--labels] [--video] [--video-bg R,G,B] <cgp_string> <output.png>")
        print("   or: python3 render_board.py [--theme THEME] [--supersample N] [--labels] [--video] [--video-bg R,G,B] --file <position.cgp> <output.png>")
        print("   or: python3 render_board.py --debug <output.png>")
        print("\nAvailable themes: dark-theme (default), light-theme")
        print("Supersample: 1 (default, fast), 4 (high quality)")
        print("--labels: Show row/column labels (A-O, 1-15)")
        print("--video: Render centered in 1920x1080 landscape frame for video")
        print("--video-bg: Background color for video mode (default: 100,32,128)")
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    theme_name = None
    supersample = 1
    show_labels = False
    video_mode = False
    video_bg = (100, 32, 128)

    # Check for --theme flag
    if '--theme' in args:
        theme_idx = args.index('--theme')
        if theme_idx + 1 >= len(args):
            print("Error: --theme requires a theme name", file=sys.stderr)
            sys.exit(1)
        theme_name = args[theme_idx + 1]
        # Remove --theme and its argument
        args = args[:theme_idx] + args[theme_idx + 2:]

    # Check for --supersample flag
    if '--supersample' in args:
        ss_idx = args.index('--supersample')
        if ss_idx + 1 >= len(args):
            print("Error: --supersample requires a value", file=sys.stderr)
            sys.exit(1)
        try:
            supersample = int(args[ss_idx + 1])
        except ValueError:
            print("Error: --supersample value must be an integer", file=sys.stderr)
            sys.exit(1)
        # Remove --supersample and its argument
        args = args[:ss_idx] + args[ss_idx + 2:]

    # Check for --labels flag
    if '--labels' in args:
        show_labels = True
        args.remove('--labels')

    # Check for --video flag
    if '--video' in args:
        video_mode = True
        args.remove('--video')

    # Check for --video-bg flag
    if '--video-bg' in args:
        bg_idx = args.index('--video-bg')
        if bg_idx + 1 >= len(args):
            print("Error: --video-bg requires R,G,B values", file=sys.stderr)
            sys.exit(1)
        try:
            rgb_parts = args[bg_idx + 1].split(',')
            if len(rgb_parts) != 3:
                raise ValueError("Must provide exactly 3 values")
            video_bg = tuple(int(x) for x in rgb_parts)
            if not all(0 <= x <= 255 for x in video_bg):
                raise ValueError("RGB values must be 0-255")
        except ValueError as e:
            print(f"Error: Invalid --video-bg format: {e}", file=sys.stderr)
            sys.exit(1)
        # Remove --video-bg and its argument
        args = args[:bg_idx] + args[bg_idx + 2:]

    # Load theme if specified
    if theme_name:
        load_theme(theme_name)

    if len(args) == 0:
        print("Error: No command provided", file=sys.stderr)
        sys.exit(1)

    if args[0] == '--debug':
        output_path = args[1] if len(args) > 1 else 'debug_squares.png'
        render_debug_squares(output_path, supersample)
    elif args[0] == '--file':
        if len(args) < 3:
            print("Error: --file requires input and output file", file=sys.stderr)
            sys.exit(1)
        with open(args[1], 'r') as f:
            cgp_string = f.read().strip()
        output_path = args[2]
        render_position(cgp_string, output_path, supersample, show_labels, video_mode, video_bg)
    else:
        if len(args) < 2:
            print("Error: Missing output file", file=sys.stderr)
            sys.exit(1)
        cgp_string = args[0]
        output_path = args[1]
        render_position(cgp_string, output_path, supersample, show_labels, video_mode, video_bg)


if __name__ == '__main__':
    main()
