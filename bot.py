import sys
import asyncio
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from playwright.async_api import async_playwright

# Фикс asyncio под Python 3.11 для Windows
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = "7786714298:AAFlqibLEF4y-LlJny2eJGYgM3wp0L__8kE"
REQUESTS_FILE = "requests.json"

# 🖥️ Главное меню с emoji
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🏪 Войти в магазин", callback_data="login")],
        [InlineKeyboardButton("🔄 Изменить активный магазин", callback_data="change_store")],
        [InlineKeyboardButton("📝 Создать заявку", callback_data="create_request")],
        [InlineKeyboardButton("📂 Мои заявки", callback_data="my_requests")],
        [InlineKeyboardButton("🔔 Подпишись на канал", callback_data="subscribe_channel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 🔙 Кнопка возврата в меню
def get_back_menu():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="main_menu")]]
    )

# 🚩 Стартовая функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я твой помощник и готов автоматизировать создание заявок на перераспределение остатков.",
        reply_markup=get_main_menu()
    )

# 🌟 Обработчик нажатий на кнопки
from subprocess import run
import sys

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match query.data:
        case "login":
            await query.edit_message_text("⏳ Проверяю авторизацию... Подождите.")

            # теперь код запускается правильно через внешний subprocess
            result = run([sys.executable, "wb_cookie_checker_sync.py"], capture_output=True, text=True)

            if result.returncode == 0:
                await query.edit_message_text("✅ Куки валидны, выполняю автоматический вход...")
                result_auto_login = run(
                    [sys.executable, "wb_auto_login.py"],
                    capture_output=True, text=True
                )
                if result_auto_login.returncode == 0:
                    await query.edit_message_text("✅ Автоматический вход успешно завершен!", reply_markup=get_back_menu())
                else:
                    await query.edit_message_text(f"⚠️ Ошибка автоматического входа:\n{result_auto_login.stderr}", reply_markup=get_back_menu())
            else:
                await query.edit_message_text("⚠️ Куки недействительны или отсутствуют.\nЗапускаю процедуру ручной авторизации...")
                result_manual_auth = run(
                    [sys.executable, "wb_auth.py"],
                    capture_output=True, text=True
                )
                if result_manual_auth.returncode == 0:
                    await query.edit_message_text("✅ Авторизация успешно завершена, куки обновлены!", reply_markup=get_back_menu())
                else:
                    await query.edit_message_text(f"❌ Ошибка ручной авторизации:\n{result_manual_auth.stderr}", reply_markup=get_back_menu())

        # остальные case не меняй, оставляй как есть
        case "change_store":
            await query.edit_message_text("🔄 Изменение активного магазина (функционал в разработке).", reply_markup=get_back_menu())

        case "create_request":
            await query.edit_message_text("📝 Создание заявки (функционал в разработке).", reply_markup=get_back_menu())

        case "my_requests":
            try:
                with open(REQUESTS_FILE, "r", encoding="utf-8") as file:
                    requests = json.load(file)

                if not requests:
                    await query.edit_message_text("📭 У вас нет созданных заявок.", reply_markup=get_back_menu())
                    return

                messages = []
                for req in requests:
                    messages.append(
                        f"📌 Артикул: {req['article']}\n"
                        f"🎲 Количество: {req['quantity']}\n"
                        f"🏬 Из: {req['from_warehouse']} ➡️ В: {req['to_warehouse']}\n"
                        f"🏷 Статус: {req['status']}"
                    )

                await query.edit_message_text("\n\n".join(messages), reply_markup=get_back_menu())
            except FileNotFoundError:
                await query.edit_message_text("📭 У вас нет созданных заявок.", reply_markup=get_back_menu())

        case "subscribe_channel":
            await query.edit_message_text("🔔 Подписка на канал (функционал в разработке).", reply_markup=get_back_menu())

        case "main_menu":
            await query.edit_message_text(
                "👋 Главное меню, выберите нужное действие:",
                reply_markup=get_main_menu()
            )


# 🚀 Основная функция запуска
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    print("🤖✅ Бот запущен и готов к работе...")
    application.run_polling()

if __name__ == "__main__":
    main()

