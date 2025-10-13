"""
Tile rendering utilities extracted from render_board.py.
Can be used to render individual Scrabble tiles.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import os

# Tile sizing constants (at 1x scale)
BASE_TILE_SIZE = 63
TILE_FRACTION = 0.88
CORNER_RADIUS_FRACTION = 0.25
GRADIENT_FRACTION = 0.98

# Point values for letters
LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
    'Y': 4, 'Z': 10
}

# Default tile color
TILE_COLOR = (245, 230, 190)
LETTER_COLOR = (0, 0, 0)

def round_corners_with_paint(draw: ImageDraw.Draw, bbox: Tuple[int, int, int, int],
                            radius: int, bg_color: Tuple[int, int, int]):
    """
    Round corners by painting background color to mask the sharp corners.
    We draw a circle at each corner and paint the OUTSIDE quarter (the corner of the square).
    """
    import math
    x1, y1, x2, y2 = bbox

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


def apply_gradient(img: Image.Image, bbox: Tuple[int, int, int, int], intensity: float = 0.18):
    """Apply concave gradient to tile area."""
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    pixels = img.load()
    has_alpha = img.mode == 'RGBA'

    for py in range(y1, y2):
        for px in range(x1, x2):
            # Distance from center (normalized)
            dx = (px - (x1 + width/2)) / (width/2)
            dy = (py - (y1 + height/2)) / (height/2)
            dist = (dx*dx + dy*dy) ** 0.5

            # Concave gradient (darker at edges)
            factor = min(1.0, dist)
            gradient_value = int(255 * (1 - intensity * factor))

            # Apply to existing pixel
            if has_alpha:
                r, g, b, a = pixels[px, py]
            else:
                r, g, b = pixels[px, py]

            opacity = intensity
            r = int(r * (1 - opacity) + gradient_value * opacity)
            g = int(g * (1 - opacity) + gradient_value * opacity)
            b = int(b * (1 - opacity) + gradient_value * opacity)

            if has_alpha:
                pixels[px, py] = (r, g, b, a)
            else:
                pixels[px, py] = (r, g, b)


def render_tile(letter: str, scale: int = 1, tile_color: Tuple[int, int, int] = TILE_COLOR,
                letter_color: Tuple[int, int, int] = LETTER_COLOR,
                bg_color: Tuple[int, int, int] = (235, 232, 217),
                transparent: bool = False) -> Image.Image:
    """
    Render a single Scrabble tile with letter and point value.

    Args:
        letter: Letter to render (A-Z, or lowercase for blank)
        scale: Render scale (1 for 63px, 4 for 252px, etc)
        tile_color: RGB color for tile background
        letter_color: RGB color for letter and point value
        bg_color: RGB color for image background (ignored if transparent=True)
        transparent: If True, use RGBA with transparent background

    Returns:
        PIL Image of the tile
    """
    tile_size_full = BASE_TILE_SIZE * scale
    tile_size = int(tile_size_full * TILE_FRACTION)
    corner_radius = int(tile_size * CORNER_RADIUS_FRACTION)
    gradient_size = int(tile_size * GRADIENT_FRACTION)
    gradient_offset = (tile_size - gradient_size) // 2

    # Create image with transparency if requested
    if transparent:
        img = Image.new('RGBA', (tile_size_full, tile_size_full), (0, 0, 0, 0))
    else:
        img = Image.new('RGB', (tile_size_full, tile_size_full), bg_color)
    draw = ImageDraw.Draw(img)

    # Calculate position (centered)
    tile_margin = (tile_size_full - tile_size) // 2
    x = tile_margin
    y = tile_margin

    # Draw tile square
    draw.rectangle([x, y, x + tile_size, y + tile_size], fill=tile_color)

    # Apply gradient
    grad_x = x + gradient_offset
    grad_y = y + gradient_offset
    apply_gradient(img, (grad_x, grad_y, grad_x + gradient_size, grad_y + gradient_size), 0.18)

    # Round corners (use transparent or bg_color)
    corner_color = (0, 0, 0, 0) if transparent else bg_color
    round_corners_with_paint(draw, (x, y, x + tile_size, y + tile_size), corner_radius, corner_color)

    # Load fonts
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        font_letter = ImageFont.truetype(os.path.join(font_dir, 'ClearSans-Bold.ttf'), int(48 * scale * 0.7145))
        font_value = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), int(22 * scale))
    except:
        font_letter = ImageFont.load_default()
        font_value = ImageFont.load_default()

    # Check if blank (lowercase)
    is_blank = letter.islower()
    display_letter = letter.upper()

    # Draw letter
    letter_offset_up = 0.05
    letter_x = grad_x + gradient_size // 2
    letter_y = grad_y + int(gradient_size * (0.5 - letter_offset_up))

    if is_blank:
        # Draw blank outline
        blank_size = int(gradient_size * 0.6667)
        blank_x = letter_x - blank_size // 2
        blank_y = letter_y - blank_size // 2
        blank_radius = int(blank_size * 0.25)
        blank_width = 2 * scale
        draw.rounded_rectangle(
            [(blank_x, blank_y), (blank_x + blank_size, blank_y + blank_size)],
            radius=blank_radius,
            outline=letter_color,
            width=blank_width
        )

    draw.text((letter_x, letter_y), display_letter, fill=letter_color, font=font_letter, anchor='mm')

    # Draw point value (only for non-blank)
    if not is_blank:
        value = str(LETTER_VALUES.get(display_letter, 0))

        # Font size based on digit count
        if len(value) == 1:
            font_val_sized = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'),
                                               int(22 * scale * 0.3192)) if os.path.exists(os.path.join(font_dir, 'Roboto-Bold.ttf')) else font_value
            h_offset = 0.88
            adjust_x, adjust_y = (-2 * scale, -2 * scale)
        else:
            font_val_sized = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'),
                                               int(22 * scale * 0.2452)) if os.path.exists(os.path.join(font_dir, 'Roboto-Bold.ttf')) else font_value
            h_offset = 0.82
            adjust_x, adjust_y = (1 * scale, -1 * scale)

        val_x = grad_x + int(h_offset * gradient_size) + adjust_x
        val_y = grad_y + int(0.80 * gradient_size) + adjust_y

        draw.text((val_x, val_y), value, fill=letter_color, font=font_val_sized, anchor='mm')

    return img
