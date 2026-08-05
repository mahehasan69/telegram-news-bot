from PIL import Image, ImageDraw, ImageFont
import textwrap
import os


WIDTH = 1280
HEIGHT = 720


def create_news_card(
    image_path,
    title,
    category,
    breaking,
    output="news_card.jpg",
):

    img = Image.open(image_path).convert("RGB")
    img = img.resize((WIDTH, HEIGHT))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))

    draw = ImageDraw.Draw(overlay)

    # Dark gradient area
    draw.rectangle(
        (0, 420, WIDTH, HEIGHT),
        fill=(0, 0, 0, 170),
    )

    try:
        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            52,
        )

        small_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            34,
        )

    except:

        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Breaking Banner
    draw.rounded_rectangle(
        (40, 30, 420, 95),
        radius=18,
        fill=(220, 0, 0),
    )

    draw.text(
        (65, 46),
        breaking.replace("<b>", "").replace("</b>", ""),
        fill="white",
        font=small_font,
    )

    # Category
    draw.rounded_rectangle(
        (40, 110, 320, 165),
        radius=18,
        fill=(0, 102, 255),
    )

    draw.text(
        (60, 124),
        category,
        fill="white",
        font=small_font,
    )

    # Title
    y = 455

    for line in textwrap.wrap(title, width=34):

        draw.text(
            (50, y),
            line,
            fill="white",
            font=title_font,
        )

        y += 58

    # Watermark
    draw.text(
        (WIDTH - 360, HEIGHT - 60),
        "SYSTEMIC NEWS",
        fill=(255, 255, 255),
        font=small_font,
    )

    final = Image.alpha_composite(
        img.convert("RGBA"),
        overlay,
    )

    final.convert("RGB").save(
        output,
        quality=95,
    )

    return output
