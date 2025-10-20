from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import os


def try_load_font(preferred_paths: List[str], size: int) -> ImageFont.FreeTypeFont:
    for path in preferred_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        test_line = (" ".join(current_line + [word])).strip()
        line_width, _ = measure_text(draw, test_line, font)
        if line_width <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def draw_wrapped_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, x: int, y: int, width: int, fill: Tuple[int, int, int]) -> int:
    lines = wrap_text(draw, text, font, width)
    _, line_height = measure_text(draw, "Ag", font)
    line_height = int(line_height * 1.25)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def make_poster(output_path: str) -> None:
    WIDTH, HEIGHT = 1200, 1200  # LinkedIn-friendly square
    MARGIN = 80

    # Color palette (slate + cyan/violet accents)
    BG = (15, 23, 42)          # slate-900
    PANEL = (30, 41, 59)       # slate-800
    TEXT = (248, 250, 252)     # slate-50
    MUTED = (203, 213, 225)    # slate-300
    ACCENT = (34, 211, 238)    # cyan-400
    ACCENT_2 = (167, 139, 250) # violet-400
    DIVIDER = (51, 65, 85)     # slate-700

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Fonts (attempt common Linux paths, fallback to default)
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    title_font = try_load_font(bold_candidates, 80)
    subtitle_font = try_load_font(regular_candidates, 36)
    section_font = try_load_font(bold_candidates, 42)
    bullet_font = try_load_font(regular_candidates, 28)
    footer_font = try_load_font(regular_candidates, 24)

    # Header panel
    header_height = 190
    draw.rounded_rectangle(
        (MARGIN, MARGIN, WIDTH - MARGIN, MARGIN + header_height),
        radius=28,
        fill=PANEL,
    )

    # Title and subtitle
    title_text = "HLD vs LLD"
    subtitle_text = "High-Level Design vs Low-Level Design"

    # Decorative accent bar
    accent_bar_width = 10
    draw.rounded_rectangle(
        (MARGIN + 28, MARGIN + 28, MARGIN + 28 + accent_bar_width, MARGIN + header_height - 28),
        radius=8,
        fill=ACCENT,
    )

    # Title text
    title_x = MARGIN + 28 + accent_bar_width + 24
    title_y = MARGIN + 36
    draw.text((title_x, title_y), title_text, font=title_font, fill=TEXT)

    # Subtitle
    _, title_h = measure_text(draw, title_text, title_font)
    sub_y = title_y + title_h + 10
    draw.text((title_x, sub_y), subtitle_text, font=subtitle_font, fill=MUTED)

    # Main content area
    content_top = MARGIN + header_height + 40
    content_bottom = HEIGHT - MARGIN - 110

    # Panel background for content
    draw.rounded_rectangle(
        (MARGIN, content_top - 20, WIDTH - MARGIN, content_bottom + 20),
        radius=28,
        outline=DIVIDER,
        width=2,
        fill=None,
    )

    # Columns
    column_gap = 40
    column_width = (WIDTH - 2 * MARGIN - column_gap) // 2
    left_x = MARGIN + 28
    right_x = left_x + column_width + column_gap

    # Vertical divider
    draw.line(
        (left_x + column_width + column_gap // 2, content_top, left_x + column_width + column_gap // 2, content_bottom),
        fill=DIVIDER,
        width=2,
    )

    # Content
    hld_header = "High-Level Design (HLD)"
    lld_header = "Low-Level Design (LLD)"

    hld_points = [
        "Purpose: Big-picture architecture; how the system is structured.",
        "Scope: Boundaries, major components, tech choices, data flow, integration.",
        "Audience: Architects, tech leads, stakeholders for alignment.",
        "Deliverables: System context, C4 Containers, major data models, sequence overviews.",
        "When: Early phase; for feasibility, estimates, and risk identification.",
        "Examples: Microservices + event bus; read replicas; CDN for static assets.",
    ]

    lld_points = [
        "Purpose: Internal design of each component to implement requirements.",
        "Scope: Class and module design, APIs, DB schema, algorithms, edge cases.",
        "Audience: Developers implementing features and writing tests.",
        "Deliverables: Class diagrams, method signatures, state models, error handling, migrations.",
        "When: After HLD; directly before and during implementation.",
        "Examples: OrderService methods, retries/idempotency; DB indexes and constraints.",
    ]

    # Draw HLD column
    y_cursor = content_top
    draw.text((left_x, y_cursor), hld_header, font=section_font, fill=ACCENT)
    _, header_h = measure_text(draw, hld_header, section_font)
    y_cursor += header_h + 16

    bullet_indent = 26
    bullet_gap = 16
    bullet_symbol = "•"

    for point in hld_points:
        draw.text((left_x, y_cursor), bullet_symbol, font=bullet_font, fill=TEXT)
        y_cursor = draw_wrapped_text(
            draw,
            point,
            bullet_font,
            left_x + bullet_indent,
            y_cursor,
            column_width - bullet_indent,
            TEXT,
        )
        y_cursor += bullet_gap

    # Draw LLD column
    y_cursor_r = content_top
    draw.text((right_x, y_cursor_r), lld_header, font=section_font, fill=ACCENT_2)
    _, header_h_r = measure_text(draw, lld_header, section_font)
    y_cursor_r += header_h_r + 16

    for point in lld_points:
        draw.text((right_x, y_cursor_r), bullet_symbol, font=bullet_font, fill=TEXT)
        y_cursor_r = draw_wrapped_text(
            draw,
            point,
            bullet_font,
            right_x + bullet_indent,
            y_cursor_r,
            column_width - bullet_indent,
            TEXT,
        )
        y_cursor_r += bullet_gap

    # Tip strip
    tip_text = "Tip: Iterate — HLD informs LLD; LLD feedback can refine HLD."
    tip_y = content_bottom + 30
    draw.rounded_rectangle(
        (MARGIN, tip_y - 12, WIDTH - MARGIN, tip_y + 44),
        radius=16,
        fill=PANEL,
    )
    draw.text((MARGIN + 28, tip_y), tip_text, font=subtitle_font, fill=MUTED)

    # Footer / watermark
    footer_text_left = "Designed for LinkedIn 1200×1200"
    footer_text_right = "#SystemDesign  #HLD  #LLD"

    _, footer_h = measure_text(draw, footer_text_left, footer_font)
    footer_y = HEIGHT - MARGIN - footer_h

    draw.text((MARGIN, footer_y), footer_text_left, font=footer_font, fill=MUTED)
    right_text_w, _ = measure_text(draw, footer_text_right, footer_font)
    draw.text((WIDTH - MARGIN - right_text_w, footer_y), footer_text_right, font=footer_font, fill=MUTED)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Poster generated: {output_path}")


if __name__ == "__main__":
    default_output = os.path.join("assets", "hld_vs_lld_linkedin.png")
    make_poster(default_output)
