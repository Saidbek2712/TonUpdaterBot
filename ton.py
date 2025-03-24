import asyncio
import logging
import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "7816335685:AAE8kTWawN_YHs1VQoAAdt9owGv9nLZEqMY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

TOKENS = {
    "TON": "TONUSDT",
    "NOT": "NOTUSDT",
}

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    price = float(data["lastPrice"])
    change_24h = float(data["priceChangePercent"])
    return price, change_24h

def get_price_history(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=24"
    response = requests.get(url)
    data = response.json()
    times = [datetime.datetime.fromtimestamp(int(entry[0]) / 1000) for entry in data]
    prices = [float(entry[4]) for entry in data]
    return times, prices

def create_price_chart(symbol):
    times, prices = get_price_history(symbol)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(times, prices, color="#00FF66", linewidth=2)
    ax.set_facecolor("#131722")
    ax.tick_params(axis="x", colors="white", rotation=30)
    ax.tick_params(axis="y", colors="white")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
    ax.set_title("Цена за 24 часа", color="white", fontsize=14)

    file_path = f"{symbol}_chart.png"
    plt.savefig(file_path, bbox_inches="tight", facecolor="#131722")
    plt.close()
    return file_path

@dp.message(Command("start"))
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Цена TON 💎"), KeyboardButton(text="Цена NOT 🪙")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите монету, чтобы узнать её цену:", reply_markup=keyboard)

@dp.message(lambda message: message.text.startswith("Цена "))
async def check_price(message: Message):
    coin_name = message.text.split(" ")[1]
    if coin_name in TOKENS:
        price, change_24h = get_price(TOKENS[coin_name])
        file_path = create_price_chart(TOKENS[coin_name])

        caption = f"💰 Цена {coin_name}: {price:.4f} USDT\n📊 Изменение за 24 часа: {change_24h:.2f}%"
        await message.answer_photo(photo=types.FSInputFile(file_path), caption=caption)
    else:
        await message.answer("Неизвестная монета. Выберите из доступных кнопок.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
