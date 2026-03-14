import os
import re
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL


CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def resize_keep_ratio(max_w, max_h, img):
    w_ratio = max_w / img.size[0]
    h_ratio = max_h / img.size[1]
    new_w = int(w_ratio * img.size[0])
    new_h = int(h_ratio * img.size[1])
    return img.resize((new_w, new_h))


async def get_thumb(videoid):

    final_path = f"{CACHE_DIR}/{videoid}.png"

    if os.path.exists(final_path):
        return final_path

    try:

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)

        for result in (await results.next())["result"]:

            title = result.get("title", "Unknown Title")
            title = re.sub(r"\W+", " ", title).title()

            duration = result.get("duration", "Unknown")

            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown"

            thumb_url = result["thumbnails"][0]["url"].split("?")[0]

        thumb_path = f"{CACHE_DIR}/thumb_{videoid}.png"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(thumb_path)

        bg = resize_keep_ratio(1280, 720, youtube)
        bg = bg.filter(ImageFilter.GaussianBlur(25))
        bg = ImageEnhance.Brightness(bg).enhance(0.4)

        width = 840
        height = 460
        cover = youtube.resize((width, height))

        mask = Image.new("L", (width, height), 0)
        draw_mask = ImageDraw.Draw(mask)

        draw_mask.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=25,
            fill=255
        )

        cover.putalpha(mask)

        center_x = 640
        center_y = 300

        x = center_x - width // 2
        y = center_y - height // 2

        bg.paste(cover, (x, y), cover)

        draw = ImageDraw.Draw(bg)

        try:
            title_font = ImageFont.truetype("AloneMusic/assets/font.ttf", 45)
            stats_font = ImageFont.truetype("AloneMusic/assets/font2.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            stats_font = ImageFont.load_default()

        if len(title) > 45:
            title = title[:45] + "..."

        text_y = y + height + 50

        w = draw.textlength(title, font=title_font)

        draw.text(
            ((1280 - w) / 2, text_y),
            title,
            fill="white",
            font=title_font,
            stroke_width=1,
            stroke_fill="black"
        )

        stats = f"Views: {views} | Duration: {duration}"

        w2 = draw.textlength(stats, font=stats_font)

        draw.text(
            ((1280 - w2) / 2, text_y + 70),
            stats,
            fill="#ff0099",
            font=stats_font,
            stroke_width=1,
            stroke_fill="black"
        )

        bg.save(final_path)

        try:
            os.remove(thumb_path)
        except:
            pass

        return final_path

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL


async def get_qthumb(videoid):

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)

        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        return thumbnail

    except Exception:
        return YOUTUBE_IMG_URL
