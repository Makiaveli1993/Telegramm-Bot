import json
from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    # Открываем новую страницу
    context = browser.new_context()

    # Загружаем сохранённые ранее куки для авторизации
    with open("wb_cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
        context.add_cookies(cookies)

    # С открытыми куками открываем сайт, больше СМС не нужно!
    page = context.new_page()

    # ✅ Переходим сразу на страницу продавца Wildberries (Личный кабинет продавца)
    page.goto("https://seller.wildberries.ru/")

    # Проверяем, успешно ли авторизовались
    sleep(5)  # Даем страничке загрузиться полностью

    # Если вы находитесь на seller-странице - успех
    if "seller.wildberries.ru" in page.url:
        print("🚀✅ Автоматический вход через куки прошел успешно! Без СМС!")

    else:
        print("❌ Не удалось авторизоваться через куки. Возможно, куки устарели. Пройдите авторизацию вручную заново.")

    browser.close()