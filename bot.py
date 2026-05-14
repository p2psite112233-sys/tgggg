import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== РОЛИ (простая система) ======
ADMINS = set()     # можно добавить свой ID
WORKERS = set()    # работники

# ====== ЗАЯВКИ ======
orders = {}
order_id = 1

# ====== МЕНЮ ======
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Карта под оплату")],
            [KeyboardButton(text="📋 Мои заявки")],
            [KeyboardButton(text="🧑‍💼 Взять заявку (worker)")],
        ],
        resize_keyboard=True
    )

# ====== /start ======
@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Бот запущен 🚀", reply_markup=main_menu())

# ====== СОЗДАТЬ ЗАЯВКУ ======
@dp.message(F.text == "💳 Карта под оплату")
async def create_order(message: types.Message):
    global order_id

    orders[order_id] = {
        "id": order_id,
        "user_id": message.from_user.id,
        "status": "NEW",
        "worker_id": None,
        "amount": None
    }

    await message.answer(f"✅ Заявка #{order_id} создана")

    order_id += 1

# ====== МОИ ЗАЯВКИ ======
@dp.message(F.text == "📋 Мои заявки")
async def my_orders(message: types.Message):
    uid = message.from_user.id

    user_orders = [
        f"#{o['id']} | {o['status']} | worker={o['worker_id']}"
        for o in orders.values()
        if o["user_id"] == uid
    ]

    if not user_orders:
        await message.answer("У тебя нет заявок")
        return

    await message.answer("\n".join(user_orders))

# ====== ВЗЯТЬ ЗАЯВКУ (WORKER SYSTEM) ======
@dp.message(F.text == "🧑‍💼 Взять заявку (worker)")
async def take_order(message: types.Message):
    uid = message.from_user.id

    # если заявка уже есть
    for o in orders.values():
        if o["status"] == "NEW":
            o["status"] = "IN_PROGRESS"
            o["worker_id"] = uid

            await message.answer(f"🟢 Ты взял заявку #{o['id']}")
            return

    await message.answer("❌ Нет свободных заявок")

# ====== ПРОСТОЙ ЧАТ В ЗАЯВКЕ ======
@dp.message()
async def fallback(message: types.Message):
    text = message.text

    # если это число → считаем сумму заявки
    if text.isdigit():
        amt = int(text)

        # создаём заявку с суммой
        global order_id
        orders[order_id] = {
            "id": order_id,
            "user_id": message.from_user.id,
            "status": "NEW",
            "worker_id": None,
            "amount": amt
        }

        await message.answer(f"💰 Заявка #{order_id} на {amt} RUB создана")
        order_id += 1
        return

    await message.answer("Используй меню 👇", reply_markup=main_menu())

# ====== ЗАПУСК ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())