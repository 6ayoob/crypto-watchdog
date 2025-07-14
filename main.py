import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from flask import Flask

# بيانات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxYxY8"
ALLOWED_USERS = [7863509137]

# إعداد Flask للـ Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return 'Crypto Watchdog is running!'

# دالة جلب بيانات عملة معينة
def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if symbol in data:
            return data[symbol]['usd']
    return None

# أمر /crypto
async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    if context.args:
        symbol = context.args[0].lower()
        price = get_crypto_price(symbol)
        if price:
            await update.message.reply_text(f"The current price of {symbol.upper()} is ${price}")
        else:
            await update.message.reply_text("Symbol not found or API error.")
    else:
        await update.message.reply_text("Usage: /crypto bitcoin")

# أمر /top (أفضل العملات)
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        msg = "Top 5 Cryptos by Market Cap:

"
        for coin in data:
            msg += f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}
"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Failed to fetch data.")

# بدء البوت
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("crypto", crypto))
    app.add_handler(CommandHandler("top", top))
    app.run_polling()
