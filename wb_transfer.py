import asyncio
import json
from playwright.async_api import async_playwright

COOKIE_FILE = "wb_cookies.json"

async def transfer_stocks(article, from_warehouse, to_warehouse, quantity):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Загружаем куки
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto("https://seller.wildberries.ru/analytics/reports/stock-remains-report")

        # Открываем окно "Перераспределить остатки"
        await page.click("text='Перераспределить остатки'")
        await page.wait_for_selector("text='Перераспределить остатки товара'", timeout=10000)

        # Заполняем поле "Артикул WB"
        await page.fill('input[placeholder="Артикул WB"]', article)
        await asyncio.sleep(1)

        # Выбираем склад "Откуда забрать"
        await page.click('div:has-text("Откуда забрать") >> input')
        await page.fill('div:has-text("Откуда забрать") >> input', from_warehouse)
        await page.keyboard.press('Enter')
        await asyncio.sleep(1)

        # Проверим лимиты (проверим сообщение о дневном лимите)
        limit_exceeded = await page.query_selector("text='Дневной лимит исчерпан. Переместите товар с другого склада или попробуйте завтра'")
        if limit_exceeded:
            print("❌ Лимит исчерпан. Автоматизация остановлена.")
            await browser.close()
            return False

        # Выбираем склад "Куда переместить"
        await page.click('div:has-text("Куда переместить") >> input')
        await page.fill('div:has-text("Куда переместить") >> input', to_warehouse)
        await page.keyboard.press('Enter')
        await asyncio.sleep(1)

        # Заполняем "Количество товара"
        await page.fill('input[placeholder="Количество товара, шт"]', str(quantity))

        # Нажимаем кнопку подтверждения перемещения (допустим, кнопка называется "Создать заявку")
        await page.click("button:has-text('Создать заявку')")

        await asyncio.sleep(3)  # Даём чуть-чуть времени на загрузку после клика

        # Тут может понадобиться проверить успешное сообщение или уведомление об успехе. Вы можете дать мне текст сообщения, если оно появляется.
        print("✅ Заявка создана успешно")
        await browser.close()
        return True

# тестовый запуск
if __name__ == "__main__":
    asyncio.run(transfer_stocks("28086636", "Тула", "Подольск", 5))