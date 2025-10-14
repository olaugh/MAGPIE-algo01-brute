#!/usr/bin/env python3
"""
Generate beautiful empty board backgrounds using render_board.py rendering code.

Creates 1920x1080 backgrounds with the same beautiful style as render_board.py
(rounded corners, gradients, premium square labels).
"""

from render_board import render_board, load_theme, THEME, BOARD_DIM, BASE_SQUARE_SIZE, get_bonus_label, get_bonus_color
from PIL import Image, ImageDraw, ImageFont
import os
import math

# Video dimensions
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

def save_board_without_canvas(board_img, output_path):
    """Save just the board image without embedding in a video canvas."""
    board_img.save(output_path)
    print(f"  Saved: {output_path} ({board_img.size[0]}x{board_img.size[1]})")


def draw_star(draw, center_x, center_y, outer_radius, inner_radius, fill):
    """Draw a 5-pointed star."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + (2 * math.pi * i / 10)  # Start at top
        if i % 2 == 0:
            # Outer point
            r = outer_radius
        else:
            # Inner point
            r = inner_radius
        x = center_x + r * math.cos(angle)
        y = center_y - r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill)


def draw_premium_labels_on_board(img, with_labels_margins=True):
    """Draw premium square labels (3W, 2W, 3L, 2L) and center star on the board image."""
    draw = ImageDraw.Draw(img)

    # Margins
    if with_labels_margins:
        margin_left = 40
        margin_top = 38
    else:
        margin_left = 40
        margin_top = 40

    square_size = BASE_SQUARE_SIZE

    # Load font for premium labels
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        premium_font = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), 16)
    except:
        premium_font = ImageFont.load_default()

    # Where the board is on the canvas
    board_size = BOARD_DIM * BASE_SQUARE_SIZE + margin_left + (13 if with_labels_margins else 40)
    board_x = (VIDEO_WIDTH - board_size) // 2
    board_y = (VIDEO_HEIGHT - board_size) // 2

    # Draw premium labels on each square
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            # Center square gets a star instead of 2W label
            if row == 7 and col == 7:
                x = board_x + margin_left + col * square_size + square_size // 2
                y = board_y + margin_top + row * square_size + square_size // 2
                # Draw white star
                draw_star(draw, x, y, outer_radius=12, inner_radius=5, fill=(255, 255, 255))
            else:
                label = get_bonus_label(row, col)
                if label:
                    x = board_x + margin_left + col * square_size + square_size // 2
                    y = board_y + margin_top + row * square_size + square_size // 2
                    draw.text((x, y), label, fill=(255, 255, 255), font=premium_font, anchor='mm')


def draw_labels_on_board(img, with_labels_margins=True):
    """Draw row/column labels on the board image."""
    draw = ImageDraw.Draw(img)

    # Margins
    if with_labels_margins:
        margin_left = 40
        margin_top = 38
    else:
        margin_left = 40
        margin_top = 40

    square_size = BASE_SQUARE_SIZE
    label_offset_top = int(margin_top * 0.75)  # Column labels
    row_label_offset = int(margin_left * 0.9)  # Row labels

    # Make labels darker - blend empty square color 60% with black
    empty_r, empty_g, empty_b = THEME['EMPTY_SQUARE']
    label_color = (int(empty_r * 0.6), int(empty_g * 0.6), int(empty_b * 0.6))

    # Load font for labels
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        label_font = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), 20)
    except:
        label_font = ImageFont.load_default()

    # Column labels (A-O) at top - draw directly on board image
    for col in range(BOARD_DIM):
        label = chr(ord('A') + col)
        x = margin_left + col * square_size + square_size // 2
        y = label_offset_top
        draw.text((x, y), label, fill=label_color, font=label_font, anchor='mm')

    # Row labels (1-15) at left - draw directly on board image
    for row in range(BOARD_DIM):
        label = str(row + 1)
        x = row_label_offset
        y = margin_top + row * square_size + square_size // 2
        draw.text((x, y), label, fill=label_color, font=label_font, anchor='rm')


def main():
    print("Generating beautiful empty board backgrounds...")
    print()

    # Load light theme
    print("Loading light theme...")
    load_theme('light-theme')

    # Load premium font for square labels (3W, 2W, etc.)
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        premium_font = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Bold.ttf'), int(16.1 * 4))
    except:
        premium_font = ImageFont.load_default()

    # Render empty board (no labels) at 4x scale for antialiasing
    print("Rendering empty board (no labels) at 4x...")
    board_img_4x = render_board(scale=4, board=None, show_labels=False, premium_font=premium_font)
    # Downsample to 1x
    board_img = board_img_4x.resize(
        (board_img_4x.width // 4, board_img_4x.height // 4),
        Image.Resampling.LANCZOS
    )
    save_board_without_canvas(board_img, 'board_assets/board_empty.png')

    # Render empty board (with labels) at 4x scale for antialiasing
    print("Rendering empty board (with labels) at 4x...")
    board_img_labeled_4x = render_board(scale=4, board=None, show_labels=True, premium_font=premium_font)
    # Downsample to 1x
    board_img_labeled = board_img_labeled_4x.resize(
        (board_img_labeled_4x.width // 4, board_img_labeled_4x.height // 4),
        Image.Resampling.LANCZOS
    )

    # Draw row/column labels directly on the board image
    print("Drawing row/column labels (A-O, 1-15)...")
    draw_labels_on_board(board_img_labeled, with_labels_margins=True)

    save_board_without_canvas(board_img_labeled, 'board_assets/board_empty_labeled.png')

    print()
    print("Done! Beautiful boards ready for fast compositing.")
    print("Theme: light-theme")
    print("Background: white")
    print("Antialiasing: 4x oversampling")
    print("Labels: A-O (columns), 1-15 (rows)")


if __name__ == '__main__':
    main()
