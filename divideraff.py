import tempfile
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

# from playwright.async_api import async_playwright
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
# from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a handler for the /start command
bot = Quart(__name__)
# bot.config['PROVIDE_AUTOMATIC_OPTIONS'] = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002110764294]  # Replace with the source channel ID
amazon_id = -1002049093974
flipkart_id = -1002124607504
meesho_id = -1002194362897
ajiomyntra_id = -1002146712649
cc_id = -1002078634799
# beauty_id = -1002046497963

amazon_keywords = ['amzn', 'amazon', 'tinyurl']
flipkart_keywords = ['fkrt', 'flipkart', 'boat', 'croma', 'tatacliq', 'fktr', 'Boat', 'Tatacliq', 'noise', 'firebolt']
meesho_keywords = ['meesho', 'shopsy', 'msho', 'wishlink']
ajio_keywords = ['ajiio', 'myntr', 'xyxx', 'ajio', 'myntra', 'mamaearth', 'bombayshavingcompany', 'beardo', 'Beardo',
                 'Tresemme', 'themancompany', 'wow', 'nykaa',
                 'mCaffeine', 'mcaffeine', 'Bombay Shaving Company', 'BSC', 'TMC', 'foxtale',
                 'fitspire', 'PUER', 'foxtaleskin', 'fitspire', 'pueronline', 'plumgoodness', 'myglamm',
                 'himalayawellness', 'biotique', 'foreo', 'vega', 'maybelline', 'lorealparis',
                 'lakmeindia', 'clinique', 'thebodyshop', 'sephora', 'naturesbasket', 'healthandglow',
                 'colorbarcosmetics', 'sugarcosmetics', 'kamaayurveda', 'forestessentialsindia', 'derma', 'clovia',
                 'zandu', 'renee', 'bellavita']
# cc_keywords=['axis','hdfc','icici','sbm','sbi','credit','idfc','aubank','hsbc','Axis','Hdfc','Icici','Sbm','Sbi','Credit','Idfc','Aubank','Hsbc',
#             'AXIS','HDFC','ICICI','SBM','SBI','CREDIT','IDFC','AUBANK','HSBC']
# cc_keywords = ['Apply Now', 'Lifetime Free', 'Apply for', ' Lifetime free', 'Benifits', 'Apply here', 'Lifetime FREE',
#                'ELIGIBILITY', 'Myzone', 'Rupay', 'rupay', 'Complimentary', 'Apply from here', 'annual fee',
#                'Annual fee', 'joining fee']

shortnerfound = ['extp', 'bitli', 'bit.ly', 'bitly', 'bitili', 'biti']

# tuple(amazon_keywords): amazon_id,
keyword_to_chat_id = {
    tuple(amazon_keywords): amazon_id,
    tuple(flipkart_keywords): flipkart_id,
    tuple(meesho_keywords): meesho_id,
    tuple(ajio_keywords): ajiomyntra_id
}
BANNER_MESSAGES = {
    -1002049093974: "🔥Search @amazon_loots_daily ❤️‍🔥",  # Replace with actual channel ID
    -1002124607504: "💥 Search @Flipkart_Loots_daily 💥",
    -1002133412234: "🛍️ Search  @Shopsy_Meesho_Deals 🛍️",
    -1002146712649: " 👗 Search @Ajio_myntra_Deals 😉"
}

def extract_link_from_text(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls[0] if urls else None


def tinycovert(text):
    unshortened_urls = {}
    urls = extract_link_from_text2(text)
    for url in urls:
        unshortened_urls[url] = tiny(url)
    for original_url, unshortened_url in unshortened_urls.items():
        text = text.replace(original_url, unshortened_url)
    return text


def tiny(long_url):
    url = 'http://tinyurl.com/api-create.php?url='

    response = requests.get(url + long_url)
    short_url = response.text
    return short_url


def extract_link_from_text2(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls


def unshorten_url2(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi


# async def unshorten_url(url):
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)
#             page = await browser.new_page()
#             await page.goto(url)
#             final_url = page.url
#             await browser.close()
#             return final_url
#     except Exception as e:
#         print(f"Error: {e}")
#         return None


def removedup(text):
    urls = re.findall(r"https?://\S+", text)
    unique_urls = []
    seen = set()

    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    # Remove duplicate URL lines
    lines = text.split("\n")
    cleaned_lines = []
    seen_urls = set()

    for line in lines:
        if any(url in line for url in unique_urls):
            # If the URL in the line is already seen, skip it
            url_in_line = next((url for url in unique_urls if url in line), None)
            if url_in_line and url_in_line in seen_urls:
                continue
            seen_urls.add(url_in_line)

        cleaned_lines.append(line)

    # Join cleaned lines back
    cleaned_text = "\n".join(cleaned_lines).strip()

    return cleaned_text


def add_banner_to_image(image, text):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    banner_height = int(height * 0.12)  # Banner size (12% of image height)

    # Create a banner overlay
    banner = Image.new("RGB", (width, banner_height), color=(255, 0, 0))  # Red banner
    draw_banner = ImageDraw.Draw(banner)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", size=int(banner_height * 0.97))  # Adjust font size
    except:
        font = ImageFont.load_default()  # Use default if arial.ttf is missing

    # Get text bounding box (new method)
    bbox = draw_banner.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Center text on the banner
    text_position = ((width - text_width) // 2, (banner_height - text_height) // 2)
    draw_banner.text(text_position, text, fill="white", font=font)

    # Append banner to image
    combined_image = Image.new("RGB", (width, height + banner_height))
    combined_image.paste(image, (0, 0))
    combined_image.paste(banner, (0, height))

    return combined_image

def findpcode(url):
    try:
        product_code_match = re.search(r"/product/([A-Za-z0-9]{10})", url)
        product_code_match2 = re.search(r'/dp/([A-Za-z0-9]{10})', url)
        product_code = product_code_match.group(1) if product_code_match else product_code_match2.group(1)
        return product_code
    except Exception as e:
        return

async def send(id, message):
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Main Channel", url="https://t.me/+HeHY-qoy3vsxYWU1"),
          InlineKeyboardButton("🏠 Deal Bots", url="https://t.me/Loots_Xpert/51")],
         [InlineKeyboardButton("⚡ Grab all Loots", url="https://t.me/Loots_Xpert/34"),
          InlineKeyboardButton("🎁 Whatsapp Deals", url="https://t.me/Loots_Xpert/33")]
         ])

    if message.photo:
        try:
            modifiedtxt = (message.caption).replace('@under_99_loot_deals', '@shopsy_meesho_Deals')

            # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            #     await message.download(file_name=temp_file.name)
            #     original_image = Image.open(temp_file.name).convert("RGB")

            # # Debug: Check if image is loaded correctly
            # if original_image is None:
            #     print("❌ Error: Image not loaded properly!")
            #     return

            # # Create a bannered image
            # banner_text = BANNER_MESSAGES.get(id, "🔥 LIMITED DEALS 🔥")  # Default message if ID is not found
            # bannered_image = add_banner_to_image(original_image, banner_text)

            # # Debug: Check if bannered image is created properly
            # if bannered_image is None:
            #     print("❌ Error: add_banner_to_image() returned None!")
            #     return

            # # Save modified image to BytesIO
            # image_bytes = BytesIO()
            # bannered_image.save(image_bytes, format="JPEG")  # ✅ Avoids 'NoneType' error
            # image_bytes.seek(0)

            # Modify caption with "Buy Now" links
            if 'tinyurl' in message.caption or 'amazon' in message.caption or 'amzn' in message.caption:
                # print('amzn working')
                urls = extract_link_from_text2(message.caption)
                Newtext = message.caption
                for url in urls:
                    pid=findpcode(unshorten_url2(url))
                    # print(pid,url)
                    if pid is not None:
                        if 'amzn' in url:
                            print('amzn in url')
                            Newtext = Newtext.replace(url, f"{url}\n\n<a href='https://www.amazon.in/gp/aws/cart/add.html?ASIN.1={pid}&Quantity.1=1&tag=oploots-21'>🛍 Add to Cart</a> | <a href='t.me/Amazon_Pricehistory_bot?start={pid}'>📊 PriceHistory</a></b>")
                        else:
                            Newtext = Newtext.replace(url, f"<b><a href={url}>Buy Now</a> \n\n<a href='https://www.amazon.in/gp/aws/cart/add.html?ASIN.1={pid}&Quantity.1=1&tag=oploots-21'>🛍 Add to Cart</a> | <a href='t.me/Amazon_Pricehistory_bot?start={pid}'>📊 PriceHistory</a></b>")
                    else:
                        if 'amzn' not in url:
                            Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')

                # print(Newtext)
                # Send the bannered image

                await app.send_photo(chat_id=id, photo=message.photo.file_id,
                                     caption=f'<b>{Newtext}</b>' + "\n\n<b>👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click here to Join All Deals</a> 👈</b>",
                                     reply_markup=Promo)
            else:
                await app.send_photo(chat_id=id, photo=message.photo.file_id,
                                     caption=f'<b>{modifiedtxt}</b>' + "\n\n<b>🛍️ 👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click here to Join All Deals</a> 👈</b>",
                                     reply_markup=Promo)

        except Exception as e:
            print(f"❌ Error in send function: {e}")



    elif message.text:
        modifiedtxt=(message.text).replace('@under_99_loot_deals', '@shopsy_meesho_Deals')
        if 'tinyurl' in message.text or 'amazon' in message.text or 'amzn' in message.text:
            urls = extract_link_from_text2(message.text)
            Newtext = message.text

            for url in urls:
                pid = findpcode(unshorten_url2(url))
                if pid is not None:
                    if 'amzn' in url:
                        Newtext = Newtext.replace(url,
                                                  f"{url}\n\n<a href='https://www.amazon.in/gp/aws/cart/add.html?ASIN.1={pid}&Quantity.1=1&tag=oploots-21'>🛍 Add to Cart</a> | <a href='t.me/Amazon_Pricehistory_bot?start={pid}'>📊 PriceHistory</a></b>")
                    else:
                        Newtext = Newtext.replace(url,
                                                  f"<b><a href={url}>Buy Now</a> \n\n<a href='https://www.amazon.in/gp/aws/cart/add.html?ASIN.1={pid}&Quantity.1=1&tag=oploots-21'>🛍 Add to Cart</a> | <a href='t.me/Amazon_Pricehistory_bot?start={pid}'>📊 PriceHistory</a></b>")
                else:
                    if 'amzn' not in url:
                        Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
            await app.send_message(chat_id=id,
                                   text=f'<b>{Newtext}</b>' + "\n\n<b>👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click here to Join All Deals</a> 👈</b>",
                                   disable_web_page_preview=True)
        else:
            await app.send_message(chat_id=id,
                                   text=f'<b>{modifiedtxt}</b>' + "\n\n<b>🛍️  👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click here to Join All Deals</a> 👈</b>",
                                   disable_web_page_preview=True)


@bot.route('/')
async def hello():
    return 'Hello, world!'


@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id, "ahaann")


@app.on_message(filters.chat(source_channel_id))
async def forward_message(client, message):
    inputvalue = ''
    if message.caption_entities:
        for entity in message.caption_entities:
            if entity.url is not None:
                inputvalue = entity.url
        # print(hyerlinkurl)
        if inputvalue == '':
            text = message.caption if message.caption else message.text
            inputvalue = text

    if message.entities:
        for entity in message.entities:
            if entity.url is not None:
                inputvalue = entity.url
        # print(hyerlinkurl)
        if inputvalue == '':
            text = message.text
            inputvalue = text

    if any(keyword in inputvalue for keyword in shortnerfound):
        # print(extract_link_from_text(inputvalue))
        # inputvalue= unshorten_url(extract_link_from_text(inputvalue))
        unshortened_urls = {}
        urls = extract_link_from_text2(inputvalue)
        for url in urls:
            # if 'extp' in url or 'bitli' in url:
            unshortened_urls[url] = unshorten_url2(url)
            # else:
                # unshortened_urls[url] = await unshorten_url(url)

        for original_url, unshortened_url in unshortened_urls.items():
            inputvalue = inputvalue.replace(original_url, unshortened_url)

    for keywords, chat_id in keyword_to_chat_id.items():
        if any(keyword in inputvalue for keyword in keywords):
            await send(chat_id, message)


@app.on_message(filters.group & filters.incoming)
async def handle_text(client, message):
    if message.photo:
        text = message.caption if message.caption else message.text
        inputvalue = text

        hyperlinkurl = []
        for entity in message.caption_entities:
            # new_entities.append(entity)
            if entity.url is not None:
                hyperlinkurl.append(entity.url)
        pattern = re.compile(r'Buy Now')

        inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')
        if "😱 Deal Time" in inputvalue:
            # Remove the part
            inputvalue = inputvalue.split("😱 Deal Time")[0]
        inputvalue = removedup(inputvalue)
        await app.send_photo(chat_id=message.chat.id, photo=message.photo.file_id, caption=f'<b>{inputvalue}</b>')
        await app.send_photo(chat_id=-1002198032644, photo=message.photo.file_id, caption=f'<b>{inputvalue}</b>')

    elif message.text:
        inputvalue = message.text
        hyperlinkurl = []
        for entity in message.entities:
            # new_entities.append(entity)
            if entity.url is not None:
                hyperlinkurl.append(entity.url)
        pattern = re.compile(r'Buy Now')

        inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')
        if "😱 Deal Time" in inputvalue:
            # Remove the part
            inputvalue = inputvalue.split("😱 Deal Time")[0]
        inputvalue = removedup(inputvalue)
        await app.send_message(chat_id=message.chat.id, text=inputvalue)
        await app.send_message(chat_id=-1002198032644, text=inputvalue)


@bot.before_serving
async def before_serving():
    await app.start()


@bot.after_serving
async def after_serving():
    await app.stop()


# if __name__ == '__main__':

# bot.run(port=8000)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run_task(host='0.0.0.0', port=8080))
    loop.run_forever()

