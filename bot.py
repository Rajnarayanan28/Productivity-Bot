import os
from dotenv import load_dotenv
import openpyxl
from telegram import Bot

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=API_TOKEN)

wb = openpyxl.load_workbook('tasks.xlsx')
ws = wb.active

chat_id = 'YOUR_CHAT_ID_HERE'  # Replace with your actual chat id

for row in ws.iter_rows(min_row=2, values_only=True):
    date, task, status = row
    if status == 'Pending':
        message = f"Reminder: {task} scheduled for {date}."
        bot.send_message(chat_id=chat_id, text=message)
