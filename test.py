import re
from playwright.async_api import async_playwright
import asyncio

from unshortenit import UnshortenIt


# Function to unshorten URLs
async def unshorten_url(url):  # Renamed to avoid conflict
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
def unshorten_url2(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi
# Function to extract URLs from text
def extract_links_from_text(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls

# Main function
async def main():
    inputvalue = '''
FAAASTT
53
🛒 https://bitli.in/i8qDgnh
    '''

    # Extract URLs
    urls = extract_links_from_text(inputvalue)
    print("Extracted URLs:", urls)

    # Unshorten URLs asynchronously
    unshortened_urls = {}
    for url in urls:
        unshortened_urls[url] =   unshorten_url2(url)  # Call the renamed function

    # Replace original URLs with unshortened ones in the input text
    for original_url, unshortened_url in unshortened_urls.items():
        inputvalue = inputvalue.replace(original_url, unshortened_url)

    # Print the updated text
    print("Updated Input Value:")
    print(inputvalue)

# Run the asynchronous main function
asyncio.run(main())
# import re
#
# text='''
# 🌟Women Fit and Flare Black
#
# Deal Price Rs.460/-
#
# MRP Rs.1,999/-
#
# 🛒 https://fkrt.co/0DFT36
#
# 🛒 https://fkrt.co/0DFT36
# '''
# def removedup(text):
#     urls = re.findall(r"https?://\S+", text)
#     unique_urls = []
#     seen = set()
#
#     for url in urls:
#         if url not in seen:
#             seen.add(url)
#             unique_urls.append(url)
#
#     # Remove duplicate URL lines
#     lines = text.split("\n")
#     cleaned_lines = []
#     seen_urls = set()
#
#     for line in lines:
#         if any(url in line for url in unique_urls):
#             # If the URL in the line is already seen, skip it
#             url_in_line = next((url for url in unique_urls if url in line), None)
#             if url_in_line and url_in_line in seen_urls:
#                 continue
#             seen_urls.add(url_in_line)
#
#         cleaned_lines.append(line)
#
#     # Join cleaned lines back
#     cleaned_text = "\n".join(cleaned_lines).strip()
#
#     return cleaned_text
#
# print(removedup(text))