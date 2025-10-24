import os
from dotenv import load_dotenv
import time
import datetime
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# State tracking for Pomodoro per user
pomodoro_state = {}

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def pomodoro_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /pomodoro <topic>")
        return
    topic = ' '.join(context.args)
    user_id = update.effective_user.id

    end_time = time.time() + 25 * 60
    pomodoro_state[user_id] = {'status': 'pomodoro', 'topic': topic, 'end_time': end_time}

    now = datetime.datetime.now().strftime('%Y-%m-%d, \n %H:%M')
    await update.message.reply_text(
    f'Session for "{topic}" has started on {now}.'
)
    await asyncio.sleep(25 * 60)

    if user_id in pomodoro_state and pomodoro_state[user_id]['status'] == 'pomodoro':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Pomodoro timer is over! Take a 7 minute break."
        )
        pomodoro_state[user_id] = {'status': 'break', 'end_time': time.time() + 7 * 60}
        await asyncio.sleep(7 * 60)
        if user_id in pomodoro_state and pomodoro_state[user_id]['status'] == 'break':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Break over, back to work?"
            )
            del pomodoro_state[user_id]

async def pomodoro_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pomodoro_state:
        await update.message.reply_text("No pomodoro or break is running.")
        return

    state = pomodoro_state[user_id]
    seconds_left = int(state['end_time'] - time.time())

    if state['status'] == 'pomodoro' and seconds_left > 0:
        await update.message.reply_text(f"Pomodoro running for '{state['topic']}'. {seconds_left//60} min {seconds_left%60} sec left.")
    elif state['status'] == 'break' and seconds_left > 0:
        await update.message.reply_text(f"Break time! {seconds_left//60} min {seconds_left%60} sec left.")
    else:
        await update.message.reply_text("No active pomodoro or break!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("pomodoro", pomodoro_start))
    app.add_handler(CommandHandler("pomodoro", pomodoro_start))
    app.add_handler(CommandHandler("pomodoro_status", pomodoro_status))
    print("Running Pomodoro Bot...")
    app.run_polling()
