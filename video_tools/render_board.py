#!/usr/bin/env python3
"""
Scrabble board renderer - generates PNG from CGP position string.

Usage:
    python3 render_board.py "cgp_string" output.png
    python3 render_board.py --file position.cgp output.png
"""

import sys
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional

# Classic Scrabble colors (from colors.h)
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

# Board layout
BOARD_DIM = 15
BASE_SQUARE_SIZE = 63  # At 1x scale
BASE_BOARD_SIZE = BOARD_DIM * BASE_SQUARE_SIZE

# Tile sizing (from raylib prototype)
TILE_FRACTION = 0.85
CORNER_RADIUS_FRACTION = 0.25
GRADIENT_FRACTION = 0.98

# Text positioning
LETTER_OFFSET_UP = 0.05
BLANK_SIZE_FRACTION = 0.6667
POINT_SIZE_1_DIGIT = 0.42
POINT_SIZE_2_DIGIT = 0.35
POINT_H_OFFSET = 0.87
POINT_V_OFFSET = 0.80

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
        return PREMIUM_RED
    if pos in BONUS_SQUARES['DWS'] or pos == (7, 7):  # Center is DWS color
        return PREMIUM_PINK
    if pos in BONUS_SQUARES['TLS']:
        return PREMIUM_DARKBLUE
    if pos in BONUS_SQUARES['DLS']:
        return PREMIUM_LIGHTBLUE
    return GRAY_20_PERCENT


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

    is_tile=True: Convex (white top → black bottom at 18% opacity) for raised tiles
    is_tile=False: Concave (black top → white at bottom at 4% opacity) for inset squares
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    # Load pixel data for direct manipulation
    pixels = img.load()

    opacity = 0.18 if is_tile else 0.04

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


def render_board(scale: int = 4, board: Optional[List[List[Optional[str]]]] = None) -> Image.Image:
    """
    Render Scrabble board and tiles at specified scale.

    Args:
        scale: Render scale multiplier (4 = 4x supersampling for antialiasing)

    Returns:
        PIL Image with board and tiles
    """
    square_size = BASE_SQUARE_SIZE * scale
    board_size = BASE_BOARD_SIZE * scale
    margin = 40 * scale

    img_width = board_size + 2 * margin
    img_height = board_size + 2 * margin

    # Create RGB image directly (no alpha channel = no anti-aliasing blending)
    img = Image.new('RGB', (img_width, img_height), GRAY_16_PERCENT)
    draw = ImageDraw.Draw(img)

    # Draw board squares with concave gradient and rounded borders (like raylib)
    tile_size = int(square_size * TILE_FRACTION)
    tile_margin = (square_size - tile_size) // 2
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            x = margin + col * square_size + tile_margin
            y = margin + row * square_size + tile_margin

            # Skip drawing colored square if there's a tile here (tile will be drawn on top)
            # BUT still draw the background shape
            if board and board[row][col]:
                # Draw background-colored square for proper masking
                draw.rectangle([x, y, x + tile_size, y + tile_size], fill=GRAY_16_PERCENT)
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
                                    corner_radius, GRAY_16_PERCENT)

    return img


def draw_tile(img: Image.Image, draw: ImageDraw.Draw, letter: str,
             row: int, col: int, scale: int,
             font_letter: ImageFont.ImageFont, font_value: ImageFont.ImageFont):
    """Draw a single tile on the board."""
    square_size = BASE_SQUARE_SIZE * scale
    margin = 40 * scale

    # Tile sizing
    tile_size = int(square_size * TILE_FRACTION)
    tile_margin = (square_size - tile_size) // 2
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)

    # Gradient region
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    x = margin + col * square_size + tile_margin
    y = margin + row * square_size + tile_margin

    is_blank = letter.islower()
    display_letter = letter.upper()

    # Draw tile background
    draw.rectangle([x, y, x + tile_size, y + tile_size], fill=GOLDEN)

    # Apply convex gradient overlay (tiles are raised)
    # MUST be done before rounding corners so gradient doesn't bleed into background
    grad_x = x + gradient_offset
    grad_y = y + gradient_offset
    apply_gradient_rgb(img, (grad_x, grad_y, grad_x + gradient_size, grad_y + gradient_size),
                      is_tile=True)

    # Round the corners by painting over them with background color
    # This MUST be last so corners are clean
    round_corners_with_paint(draw, (x, y, x + tile_size, y + tile_size),
                            corner_radius, GRAY_16_PERCENT)

    # Letter
    if is_blank:
        letter_size = int(gradient_size * BLANK_SIZE_FRACTION)
    else:
        letter_size = int(gradient_size * 0.95)

    try:
        font_sized = ImageFont.truetype(font_letter.path, letter_size)
    except:
        font_sized = font_letter

    # Get text metrics for proper centering (anchor='mm' centers both horizontally and vertically)
    letter_x = grad_x + gradient_size // 2
    letter_y = grad_y + int((0.5 - LETTER_OFFSET_UP) * gradient_size)

    draw.text((letter_x, letter_y), display_letter, fill=LETTER_COLOR, font=font_sized, anchor='mm')

    # Blank outline
    if is_blank:
        blank_offset = int(gradient_size * (1 - BLANK_SIZE_FRACTION) / 2)
        blank_size = int(gradient_size * BLANK_SIZE_FRACTION)
        blank_x = grad_x + blank_offset
        blank_y = grad_y + blank_offset
        blank_radius = int(blank_size * 0.15)
        draw_rounded_rect(draw, (blank_x, blank_y, blank_x + blank_size, blank_y + blank_size),
                         blank_radius, None, DARKRED, max(2, scale // 2))

    # Point value
    elif display_letter in LETTER_VALUES:
        value = str(LETTER_VALUES[display_letter])
        value_size = int(gradient_size * (POINT_SIZE_1_DIGIT if len(value) == 1 else POINT_SIZE_2_DIGIT))

        try:
            font_val_sized = ImageFont.truetype(font_value.path, value_size)
        except:
            font_val_sized = font_value

        val_x = grad_x + int(POINT_H_OFFSET * gradient_size)
        val_y = grad_y + int(POINT_V_OFFSET * gradient_size)

        draw.text((val_x, val_y), value, fill=LETTER_COLOR, font=font_val_sized, anchor='mm')


def render_position(cgp_string: str, output_path: str, supersample: int = 4):
    """
    Render CGP position to PNG with antialiasing.

    Args:
        cgp_string: CGP format string
        output_path: Output PNG file path
        supersample: Render at Nx resolution then downsample (default: 4)
    """
    # Parse CGP
    parts = cgp_string.strip().split()
    if len(parts) < 2 or parts[0] != 'cgp':
        raise ValueError("Invalid CGP format")

    board = parse_cgp_board(parts[1])

    # Render at high resolution (pass board so we don't draw squares under tiles)
    img = render_board(scale=supersample, board=board)
    draw = ImageDraw.Draw(img)

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
                draw_tile(img, draw, board[row][col], row, col, supersample, font_letter, font_value)

    # Downsample for antialiasing (img is already RGB)
    # Use NEAREST or BOX to avoid creating gray halos during downsampling
    final_size = BASE_BOARD_SIZE + 80  # 40px margin each side
    final_img = img.resize((final_size, final_size), Image.BOX)

    # Save
    final_img.save(output_path)
    print(f"Rendered {img.size[0]}×{img.size[1]}px → {final_size}×{final_size}px ({supersample}x supersampling)")
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
        print("Usage: python3 render_board.py <cgp_string> <output.png>")
        print("   or: python3 render_board.py --file <position.cgp> <output.png>")
        print("   or: python3 render_board.py --debug <output.png>")
        sys.exit(1)

    if sys.argv[1] == '--debug':
        output_path = sys.argv[2] if len(sys.argv) > 2 else 'debug_squares.png'
        render_debug_squares(output_path)
    elif sys.argv[1] == '--file':
        if len(sys.argv) < 4:
            print("Error: --file requires input and output file", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            cgp_string = f.read().strip()
        output_path = sys.argv[3]
        render_position(cgp_string, output_path)
    else:
        if len(sys.argv) < 3:
            print("Error: Missing output file", file=sys.stderr)
            sys.exit(1)
        cgp_string = sys.argv[1]
        output_path = sys.argv[2]
        render_position(cgp_string, output_path)


if __name__ == '__main__':
    main()
