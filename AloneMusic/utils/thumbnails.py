import os
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)


async def download(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()


def round_corners(img, radius):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius, fill=255)
    img.putalpha(mask)
    return img


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word if current else word
        w = draw.textlength(test, font=font)

        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def fit_font(draw, text, font_path, max_width, start_size=60, min_size=25):
    size = start_size

    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        w = draw.textlength(text, font=font)

        if w <= max_width:
            return font

        size -= 2

    return ImageFont.truetype(font_path, min_size)


async def get_thumb(title, user, thumb_url, user_photo=None):

    data = await download(thumb_url)
    yt = Image.open(BytesIO(data)).convert("RGB")

    bg = yt.resize((1280, 720)).filter(ImageFilter.GaussianBlur(35))
    canvas = Image.new("RGB", (1280, 720))
    canvas.paste(bg)

    draw = ImageDraw.Draw(canvas)

    # top thumbnail card
    card = yt.resize((900, 400))
    card = round_corners(card, 40)
    canvas.paste(card, (190, 90), card)

    # glass info card
    glass = Image.new("RGBA", (900, 180), (255, 255, 255, 40))
    glass = round_corners(glass, 35)
    canvas.paste(glass, (190, 520), glass)

    # avatar
    if user_photo:
        avatar_data = await download(user_photo)
        avatar = Image.open(BytesIO(avatar_data)).resize((110, 110))
    else:
        avatar = yt.resize((110, 110))

    avatar = round_corners(avatar, 25)
    canvas.paste(avatar, (220, 550), avatar)

    font_path = "AloneMusic/assets/font.ttf"
    small_font_path = "AloneMusic/assets/font2.ttf"

    try:
        title_font = fit_font(draw, title, font_path, 650)
        small_font = ImageFont.truetype(small_font_path, 28)
        power_font = ImageFont.truetype(small_font_path, 22)
    except:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        power_font = ImageFont.load_default()

    # wrap title
    lines = wrap_text(draw, title, title_font, 650)

    y = 560
    for line in lines[:2]:
        draw.text((360, y), line, font=title_font, fill="white")
        y += 45

    draw.text(
        (360, 620),
        f"Played By : {user}",
        font=small_font,
        fill="#e5e5e5"
    )

    draw.text(
        (360, 655),
        "ʑαʀᴀ ᴍᴜsɪᴄ",
        font=small_font,
        fill="#cccccc"
    )

    power = "ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍᴇᴄᴏ ʙᴏᴛs 🎧"
    w = draw.textlength(power, font=power_font)

    draw.text(
        ((1280 - w) / 2, 690),
        power,
        font=power_font,
        fill="white"
    )

    path = f"{CACHE}/thumb.png"
    canvas.save(path)

    return path
