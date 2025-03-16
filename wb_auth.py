import asyncio
import json
from playwright.async_api import async_playwright

COOKIE_FILE = "wb_cookies.json"

async def authenticate_wb(phone_number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # пока в False для отладки!
        context = await browser.new_context()
        page = await context.new_page()

        # URL авторизации WB Sellers:
        await page.goto("https://seller-auth.wildberries.ru/ru/?redirect_url=https%3A%2F%2Fseller.wildberries.ru%2Flogin%2Fru")

        # ввод номера телефона
        await page.wait_for_selector('input[data-testid="phone-input"]', timeout=30000)
        await page.fill('input[data-testid="phone-input"]', phone_number)
        await page.click('button[data-testid="submit-phone-button"]')

        # SMS-код авторизации
        code = input('Введите код авторизации WB (из SMS): ')
        await page.wait_for_selector('input[autocomplete="one-time-code"]', timeout=60000)
        await page.fill('input[autocomplete="one-time-code"]', code)

        # ⚠️ ИСПРАВЛЕНИЕ: ждем любого редиректа, после ввода SMS, ждем стабилизации загрузки
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)  # небольшая дополнительная пауза для гарантии завершения!

        # ✅ ВАЖНО: теперь проверяем URL или наличие элемента на странице
        if "seller.wildberries.ru" in page.url and "login" not in page.url:
            # сохраняем куки только если точно авторизовались
            cookies = await context.cookies()
            with open(COOKIE_FILE, 'w', encoding='utf-8') as file:
                json.dump(cookies, file, indent=2, ensure_ascii=False)

            print("✅ Авторизация успешно завершена и куки сохранены.")
        else:
            print(f"🚫 Что-то пошло не так, текущий URL: {page.url}")

        await browser.close()

if __name__ == "__main__":
    phone = input("Введите номер телефона WB: ")
    asyncio.run(authenticate_wb(phone))