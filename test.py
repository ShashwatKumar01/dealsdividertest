
import requests
from playwright.async_api import async_playwright
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
from playwright.sync_api import sync_playwright


api_id = '26566076'
api_hash = '40ce27837b95819c42cac67b46a2dc2b'
bot_token = '6810447810:AAHTehMwBCzhG2Eicu2OBvAnSoo-d9D9bYs'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a handler for the /start command
bot = Quart(__name__)
# bot.config['PROVIDE_AUTOMATIC_OPTIONS'] = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002110764294]  # Replace with the source channel ID
amazon_id = -1002049093974
flipkart_id = -1002124607504
meesho_id = -1002133412234
ajiomyntra_id = -1002146712649
cc_id = -1002078634799
# beauty_id = -1002046497963

amazon_keywords = ['amzn', 'amazon', 'tinyurl']
flipkart_keywords = ['fkrt', 'flipkart', 'boat', 'croma', 'tatacliq', 'fktr', 'Boat', 'Tatacliq','noise','firebolt']
meesho_keywords = ['meesho', 'shopsy', 'msho', 'wishlink']
ajio_keywords = ['ajiio', 'myntr', 'xyxx','ajio','myntra','mamaearth', 'bombayshavingcompany', 'beardo', 'Beardo', 'Tresemme', 'themancompany', 'wow', 'nykaa',
    'mCaffeine', 'mcaffeine','Bombay Shaving Company', 'BSC', 'TMC', 'foxtale',
    'fitspire', 'PUER','foxtaleskin', 'fitspire', 'pueronline', 'plumgoodness','myglamm',
    'himalayawellness', 'biotique', 'foreo', 'vega', 'maybelline', 'lorealparis',
    'lakmeindia', 'clinique', 'thebodyshop', 'sephora', 'naturesbasket', 'healthandglow',
    'colorbarcosmetics', 'sugarcosmetics', 'kamaayurveda', 'forestessentialsindia','derma','clovia','zandu','renee','bellavita']
# cc_keywords=['axis','hdfc','icici','sbm','sbi','credit','idfc','aubank','hsbc','Axis','Hdfc','Icici','Sbm','Sbi','Credit','Idfc','Aubank','Hsbc',
#             'AXIS','HDFC','ICICI','SBM','SBI','CREDIT','IDFC','AUBANK','HSBC']
cc_keywords = ['Apply Now', 'Lifetime Free', 'Apply for', ' Lifetime free', 'Benifits', 'Apply here', 'Lifetime FREE',
               'ELIGIBILITY', 'Myzone', 'Rupay', 'rupay', 'Complimentary', 'Apply from here', 'annual fee',
               'Annual fee', 'joining fee']

shortnerfound = ['extp', 'bitli', 'bit.ly', 'bitly', 'bitili','biti','bitiy','bitIy']

# tuple(amazon_keywords): amazon_id,
keyword_to_chat_id = {
    tuple(amazon_keywords): amazon_id,
    tuple(flipkart_keywords): flipkart_id,
    tuple(meesho_keywords): meesho_id,
    tuple(ajio_keywords): ajiomyntra_id,
    tuple(cc_keywords): cc_id
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


# def unshorten_url(short_url):
#     unshortener = UnshortenIt()
#     shorturi = unshortener.unshorten(short_url)
#     # print(shorturi)
#     return shorturi

async def unshorten_url(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            final_url = page.url
            await browser.close()
            return final_url
    except Exception as e:
        print(f"Error: {e}")
        return None

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

async def send(id, message):
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Join Main Channel", url="https://t.me/+HeHY-qoy3vsxYWU1")],
          [InlineKeyboardButton("ALL Loots", url="https://t.me/Deals_and_Discounts_Channel2/34"),
        InlineKeyboardButton("Whatsapp", url="https://t.me/Deals_and_Discounts_Channel2/33")]
         ])

    if message.photo:
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     await message.download(file_name=temp_file.name)
        #     with open(temp_file.name, 'rb') as f:
        #         photo_bytes = BytesIO(f.read())
        if 'tinyurl' in message.caption or 'amazon' in message.caption:
            urls = extract_link_from_text2(message.caption)
            Newtext = message.caption

            for url in urls:
                # newurl = await unshorten_url(url)
                Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
            await app.send_photo(chat_id=id, photo=message.photo.file_id, caption=f'<b>{Newtext}</b>'+"\n\n<b>🛍️  👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click HERE for MORE DEALS ! </a> 👈</b>",
                                 reply_markup=Promo)

        else:
            await app.send_photo(chat_id=id, photo=message.photo.file_id, caption=f'<b>{message.caption}</b>' + "\n\n<b>🛍️  👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click HERE for MORE DEALS ! </a> 👈</b>",
                                 reply_markup=Promo)




    elif message.text:
        if 'tinyurl' in message.text or 'amazon' in message.text:
            urls = extract_link_from_text2(message.text)
            Newtext = message.text

            for url in urls:
                # newurl = await unshorten_url(url)
                Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
            await app.send_message(chat_id=id, text=f'<b>{Newtext}</b>'+ "\n\n<b>🛍️  👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click HERE for MORE DEALS ! </a> 👈</b>", disable_web_page_preview=True)
        else:
            await app.send_message(chat_id=id, text=f'<b>{message.text}</b>'+"\n\n<b>🛍️  👉 <a href ='https://t.me/addlist/6R2xTLIL9JFkMWI1'>Click HERE for MORE DEALS ! </a> 👈</b>", disable_web_page_preview=True)


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
            unshortened_urls[url] = await unshorten_url(url)
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
        inputvalue=removedup(inputvalue)
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
