import asyncio
from playwright.async_api import async_playwright

async def check_cookies_async():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state="wb_cookies.json")
            page = await context.new_page()
            await page.goto("https://seller.wildberries.ru/")
            # ожидаем, появится ли важный элемент проверяющий авторизацию
            authorized = await page.query_selector("selector-который-подтверждает-вход")
            await browser.close()
            return authorized is not None
    except:
        return False

def check_cookies():
    return asyncio.run(check_cookies_async())

if __name__ == "__main__":
    if check_cookies():
        print("valid")
        exit(0)
    else:
        print("invalid")
        exit(1)