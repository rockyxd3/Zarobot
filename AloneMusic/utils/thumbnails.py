import os
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)


async def download(url):
    if not url:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()
    except:
        return None


def round_corners(img, radius):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius, fill=255)
    img.putalpha(mask)
    return img


async def get_thumb(*args):

    # default values
    title = "Unknown Song"
    user = "Unknown"
    thumb_url = None

    # support old play.py formats
    if len(args) == 1:
        videoid = args[0]
        thumb_url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"

    elif len(args) == 3:
        title, user, thumb_url = args

    elif len(args) >= 4:
        title, user, thumb_url, _ = args

    data = await download(thumb_url)

    if data:
        yt = Image.open(BytesIO(data)).convert("RGB")
    else:
        yt = Image.new("RGB", (1280, 720), (40, 40, 40))

    # background blur
    bg = yt.resize((1280, 720)).filter(ImageFilter.GaussianBlur(35))
    canvas = Image.new("RGB", (1280, 720))
    canvas.paste(bg)

    draw = ImageDraw.Draw(canvas)

    # main thumbnail card
    card = yt.resize((900, 400))
    card = round_corners(card, 40)
    canvas.paste(card, (190, 90), card)

    # glass info card
    glass = Image.new("RGBA", (900, 180), (255, 255, 255, 40))
    glass = round_corners(glass, 35)
    canvas.paste(glass, (190, 520), glass)

    # bot avatar (girl image)
    avatar_path = "AloneMusic/assets/girl.png"

    try:
        avatar = Image.open(avatar_path).resize((110, 110))
    except:
        avatar = yt.resize((110, 110))

    avatar = round_corners(avatar, 25)
    canvas.paste(avatar, (220, 550), avatar)

    # fonts
    try:
        title_font = ImageFont.truetype("AloneMusic/assets/font.ttf", 50)
        small_font = ImageFont.truetype("AloneMusic/assets/font2.ttf", 28)
        power_font = ImageFont.truetype("AloneMusic/assets/font2.ttf", 22)
    except:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        power_font = ImageFont.load_default()

    # title
    draw.text((360, 560), title, font=title_font, fill="white")

    # played by
    draw.text(
        (360, 620),
        f"Played By : {user}",
        font=small_font,
        fill="#e5e5e5"
    )

    # bot name
    draw.text(
        (360, 655),
        "ʑαʀᴀ ᴍᴜsɪᴄ",
        font=small_font,
        fill="#cccccc"
    )

    # footer
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
