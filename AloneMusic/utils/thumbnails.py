import os
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)

ASSETS = "AloneMusic/assets"


async def download(url):
    if not url:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()
    except:
        return None


def round_rect(img, radius):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius, fill=255)
    img.putalpha(mask)
    return img


def circle(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    img.putalpha(mask)
    return img


async def get_thumb(*args):

    title = "Unknown Song"
    user = "Unknown"
    thumb_url = None

    if len(args) == 1:
        videoid = args[0]
        thumb_url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"

    elif len(args) >= 3:
        title, user, thumb_url = args[:3]

    data = await download(thumb_url)

    if data:
        yt = Image.open(BytesIO(data)).convert("RGB")
    else:
        yt = Image.new("RGB", (1280, 720), (40, 40, 40))

    yt = yt.resize((1280, 720))

    # background blur
    bg = yt.filter(ImageFilter.GaussianBlur(40))

    canvas = Image.new("RGB", (1280, 720))
    canvas.paste(bg)

    draw = ImageDraw.Draw(canvas)

    # main preview card
    preview = yt.resize((820, 360))
    preview = round_rect(preview, 45)
    canvas.paste(preview, (230, 90), preview)

    # glass card
    glass = Image.new("RGBA", (820, 250), (255, 255, 255, 45))
    glass = round_rect(glass, 40)
    canvas.paste(glass, (230, 440), glass)

    # load fonts
    try:
        title_font = ImageFont.truetype(f"{ASSETS}/font.ttf", 55)
        text_font = ImageFont.truetype(f"{ASSETS}/font2.ttf", 35)
        small_font = ImageFont.truetype(f"{ASSETS}/font2.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # title
    draw.text(
        (260, 470),
        title,
        font=title_font,
        fill="white"
    )

    # played by
    draw.text(
        (260, 540),
        f"Played By : {user}",
        font=text_font,
        fill="#e6e6e6"
    )

    # avatar
    try:
        avatar = Image.open(f"{ASSETS}/girl.png").resize((120, 120))
    except:
        avatar = yt.resize((120, 120))

    avatar = circle(avatar)
    canvas.paste(avatar, (260, 585), avatar)

    # small glass card for bot name
    bot_card = Image.new("RGBA", (600, 110), (255, 255, 255, 55))
    bot_card = round_rect(bot_card, 30)
    canvas.paste(bot_card, (250, 580), bot_card)

    draw.text(
        (400, 610),
        "ʑαʀᴀ ᴍᴜsɪᴄ",
        font=text_font,
        fill="white"
    )

    draw.text(
        (400, 650),
        "ʑαʀᴀ ᴍᴜsɪᴄ",
        font=small_font,
        fill="#dddddd"
    )

    # footer
    footer = "ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍᴇᴄᴏ ʙᴏᴛs"
    w = draw.textlength(footer, font=small_font)

    draw.text(
        ((1280 - w) / 2, 690),
        footer,
        font=small_font,
        fill="white"
    )

    path = f"{CACHE}/thumb.png"
    canvas.save(path)

    return path
