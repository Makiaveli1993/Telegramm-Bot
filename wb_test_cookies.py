import asyncio
import json
from playwright.async_api import async_playwright

COOKIE_FILE = "wb_cookies.json"

async def test_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # пока False для проверки
        context = await browser.new_context()

        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto("https://seller.wildberries.ru/home")
        await page.wait_for_load_state("networkidle")

        # проверка элемента сайта в личном кабинете, лично кабинета селлеров
        if "seller.wildberries.ru/home" in page.url or await page.query_selector("div[data-testid='header-navbar']"):
            print("✅ Авторизация через куки прошла успешно!")
        else:
            print(f"🚫 Авторизация не удалась через куки! Текущий url: {page.url}")

        await browser.close()

asyncio.run(test_cookies())