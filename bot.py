import openpyxl
from telegram import Bot

wb = openpyxl.load_workbook('tasks.xlsx')
ws = wb.active

bot = Bot(token='YOUR_API_TOKEN_HERE')
chat_id = 'YOUR_CHAT_ID_HERE'

for row in ws.iter_rows(min_row=2, values_only=True):
    date, task, status = row
    if status == 'Pending':
        message = f"Reminder: {task} scheduled for {date}."
        bot.send_message(chat_id=chat_id, text=message)
