#!/usr/bin/env python3
"""
Generate beautiful letter tiles using render_board.py's rendering code.

Creates tiles with rounded corners, gradients, and proper styling.
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from render_board import draw_tile, load_theme, THEME

# Tile size (matching render_board.py)
BASE_SQUARE_SIZE = 63
TILE_FRACTION = 0.88
TILE_SIZE = int(BASE_SQUARE_SIZE * TILE_FRACTION)  # 55 pixels at 1x

def load_fonts(scale):
    """Load fonts for tile rendering."""
    font_dir = Path(__file__).parent / 'fonts'

    try:
        letter_size = int(TILE_SIZE * scale * 0.7)
        value_size = int(TILE_SIZE * scale * 0.3)
        font_letter = ImageFont.truetype(str(font_dir / 'ClearSans-Bold.ttf'), letter_size)
        font_value = ImageFont.truetype(str(font_dir / 'Roboto-Bold.ttf'), value_size)
    except Exception as e:
        print(f"Warning: Could not load fonts ({e}), using defaults", file=sys.stderr)
        font_letter = ImageFont.load_default()
        font_value = ImageFont.load_default()

    return font_letter, font_value


def generate_tile_for_letter(letter, is_blank, tile_color, scale=4):
    """
    Generate a single letter tile using render_board.py's draw_tile function.

    Args:
        letter: Letter to render (A-Z)
        is_blank: True if blank tile
        tile_color: RGB tuple for tile background color
        scale: Oversampling factor (4 = 4x for antialiasing)

    Returns:
        PIL Image of the tile (RGB with white background, BASE_SQUARE_SIZE x BASE_SQUARE_SIZE)
        The tile graphic is TILE_SIZE centered within the BASE_SQUARE_SIZE square
    """
    # Render the tile graphic at high resolution for antialiasing
    tile_size_scaled = TILE_SIZE * scale
    square_size_scaled = BASE_SQUARE_SIZE * scale

    # Temporarily override tile color
    original_color = THEME['TILE']
    THEME['TILE'] = tile_color

    # Load fonts
    font_letter, font_value = load_fonts(scale)

    # Create full square-sized image with theme background color (not white!)
    bg_color = THEME['BACKGROUND']
    temp_img = Image.new('RGB', (square_size_scaled, square_size_scaled), bg_color)
    draw = ImageDraw.Draw(temp_img)

    # Draw the tile at scaled size, centered in the square
    # draw_tile expects row=0, col=0 and will calculate position as:
    # x = margin_left + col * square_size + tile_margin
    # We want the tile centered, so: x = (square_size - tile_size) / 2
    # Therefore: margin_left = (square_size - tile_size) / 2 - tile_margin
    # But draw_tile already adds tile_margin, so we just pass margin_left = 0
    # and it will position at: 0 + 0 * square_size + tile_margin = tile_margin (correct!)
    display_letter = letter.lower() if is_blank else letter
    draw_tile(temp_img, draw, display_letter, 0, 0, scale, font_letter, font_value,
              margin_left=0, margin_top=0)

    # Downsample to 1x with antialiasing (keep as RGB, no alpha channel needed)
    tile_1x = temp_img.resize((BASE_SQUARE_SIZE, BASE_SQUARE_SIZE), Image.Resampling.LANCZOS)

    # Restore original tile color
    THEME['TILE'] = original_color

    return tile_1x


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python3 generate_beautiful_tiles.py <tile_color_rgb>")
        print("Example: python3 generate_beautiful_tiles.py 240,220,180")
        print("         (generates golden tiles)")
        sys.exit(1)

    # Parse color
    color_str = sys.argv[1]
    try:
        r, g, b = map(int, color_str.split(','))
        tile_color = (r, g, b)
    except:
        print(f"Error: Invalid color format. Use R,G,B like: 240,220,180", file=sys.stderr)
        sys.exit(1)

    output_dir = Path("board_assets/tiles")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating beautiful tiles with color RGB{tile_color}...")
    print(f"Output: {output_dir}")
    print()

    # Load light theme (render_board.py default is dark theme)
    load_theme('light-theme')

    # Generate letter tiles (A-Z)
    print("Generating letter tiles (A-Z)...")
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        tile = generate_tile_for_letter(letter, False, tile_color)
        tile.save(output_dir / f"letter_{letter}.png")

    # Generate blank tiles (a-z)
    print("Generating blank tiles (a-z)...")
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        tile = generate_tile_for_letter(letter, True, tile_color)
        tile.save(output_dir / f"blank_{letter.lower()}.png")

    print()
    print(f"Generated 52 beautiful tiles!")
    print(f"Tile color: RGB{tile_color}")


if __name__ == "__main__":
    main()
