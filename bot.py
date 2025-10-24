import os
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Dictionary to store sessions
pomodoro_sessions = {}  # {user_id: {status, topic, end_time, timer, break_timer}}

# Helper: minutes left
def minutes_left(end_time):
    return round((end_time - time.time()) / 60, 1)


async def pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    # Case 1: No argument
    if not args:
        await update.message.reply_text(
            "Usage: /pomodoro <topic>, /pomodoro status, or /pomodoro clear"
        )
        return

    arg = " ".join(args).strip().lower()

    # Case 2: Reserved subcommands
    if arg in ["status", "clear"]:
        if user_id not in pomodoro_sessions:
            await update.message.reply_text(
                "No session running. Start one first with /pomodoro <topic>."
            )
            return

        session = pomodoro_sessions[user_id]

        if arg == "status":
            if session["status"] != "pomodoro":
                await update.message.reply_text(
                    "No pomodoro session is currently running."
                )
                return
            left = minutes_left(session["end_time"])
            await update.message.reply_text(
                f'Session "{session["topic"]}" is currently running.\n'
                f"You have {left} minute(s) left."
            )
            return

        if arg == "clear":
            if session.get("timer"):
                session["timer"].cancel()
            if session.get("break_timer"):
                session["break_timer"].cancel()
            del pomodoro_sessions[user_id]
            await update.message.reply_text("All sessions cleared.")
            return

    # Case 3: Don't allow a new session if one is running
    if user_id in pomodoro_sessions:
        await update.message.reply_text(
            "Finish or clear your current session before starting a new one."
        )
        return

    # Case 4: Prevent 'status' or 'clear' as a topic
    if arg in ["status", "clear"]:
        await update.message.reply_text(
            "Topic cannot be 'status' or 'clear'. Please enter a valid topic."
        )
        return

    # Case 5: Start new Pomodoro session
    start_time = datetime.now()
    end_time = time.time() + 25 * 60  # 25 minutes

    def pomodoro_done():
        context.application.create_task(
            update.message.reply_text("Pomodoro timer is over! Take a 7 minute break.")
        )
        session["status"] = "break"
        session["end_time"] = time.time() + 7 * 60

        def break_done():
            context.application.create_task(
                update.message.reply_text("Break over, back to work?")
            )
            pomodoro_sessions.pop(user_id, None)

        session["break_timer"] = threading.Timer(7 * 60, break_done)
        session["break_timer"].start()

    timer = threading.Timer(25 * 60, pomodoro_done)

    session = {
        "status": "pomodoro",
        "topic": arg,
        "end_time": end_time,
        "timer": timer,
        "break_timer": None,
    }
    pomodoro_sessions[user_id] = session
    timer.start()

    await update.message.reply_text(
        f'Session for "{arg}" has started on {start_time.strftime("%Y-%m-%d, %H:%M:%S")}.'
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pomodoro Bot is running! Use /pomodoro <topic> to start.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pomodoro", pomodoro))

    print("Running Pomodoro Bot (Python)...")
    app.run_polling()
