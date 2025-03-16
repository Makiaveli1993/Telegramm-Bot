import asyncio
import json
from playwright.async_api import async_playwright

COOKIE_FILE = "wb_cookies.json"

async def check_wb_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # запускаем без окна
        context = await browser.new_context()

        # Попробуем загрузить куки из файла
        try:
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ Файл с cookies не найден или повреждён.")
            return False 

        # открываем страницу личного кабинета для проверки куки
        page = await context.new_page()
        await page.goto("https://seller.wildberries.ru/home")
        await page.wait_for_load_state("networkidle")

        # проверка наличия элемента, гарантированно говорящего об успешной авторизации
        authorized_selector = "div[data-testid='header-navbar']"
        is_authorized = await page.query_selector(authorized_selector) is not None
        await browser.close()

        if is_authorized:
            print("✅ Cookies валидны, авторизация пройдена.")
        else:
            print("❌ Cookies невалидны, авторизация отсутствует или истекла.")

        return is_authorized

# для теста функции отдельно
if __name__ == "__main__":
    auth_valid = asyncio.run(check_wb_cookies())
    print(f"Результат проверки cookies: {auth_valid}")