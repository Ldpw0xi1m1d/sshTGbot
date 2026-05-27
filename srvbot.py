import os
from dotenv import load_dotenv
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

load_dotenv()

token = os.getenv("BOT_TOKEN")
#ssh_hostname = os.getenv("SSH_HOSTNAME")
ssh_hostname = "host.docker.internal"

def ssh_command(command: str) -> str:

    try:
        result = subprocess.run(
        ["ssh", ssh_hostname, command],
        capture_output=True,
        text=True,
        timeout=20
    )
        if result.stdout:
            return result.stdout
        elif result.stderr:
            return f"Ошибка:\n{result.stderr}"
        else:
            return "Команда выполнена!"
    except subprocess.TimeoutExpired:
        return "Выполнение команды превышено"
    except Exception as e:
        return f"Ошибка: {e}"
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Статус сервера", callback_data="status")],
        [InlineKeyboardButton("Перезагрузка сервера", callback_data="reboot")],
        [InlineKeyboardButton("Показать логи сервера", callback_data="logs")],
        [InlineKeyboardButton("Свободная память", callback_data="df -h")],
        [InlineKeyboardButton("Пользовательская команда", callback_data="custom_command")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "*SSH Бот* \n Выберите команду:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    command = query.data

    if command == "status":
        command = "uptime && who -b"
    elif command == "reboot":
        keyboard = [
            [InlineKeyboardButton("Перезагрузить", callback_data="confirm_reboot")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Точно есть необходимость в перезагрузке?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    elif command == "confirm_reboot":
        command = "sudo reboot"
        await query.edit_message_text("Перезагрузка сервера...")
    elif command == "logs":
        command = "journalctl -n --no-pager"
    elif command == "custom_command":
        await query.edit_message_text(
            "Введите команду для выполнения на сервере: ",
            parse_mode="Markdown"
        )
        context.user_data['waiting_for_custom_command'] = True
        return
    elif command == "cancel":
        await query.edit_message_text("Операция отменена!")
        return
    
    await query.edit_message_text("Выполняется `{command}`", parse_mode="Markdown")

    output = ssh_command(command)

    if len(output) > 4000:
        output = output[:4000]
    
    await query.edit_message_text(f"Результат выполнения: \n ```\n{output}\n```", parse_mode="Markdown")

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_custom_command'):
        command = update.message.text
        context.user_data['waiting_for_custom_command'] = False

        await update.message.reply_text(f"Выполняется {command}", parse_mode="Markdown")
        output = ssh_command(command)

        if len(output) > 4000:
            output = output[:4000]
            
        await update.message.reply_text(f"Результат выполнения: \n ```\n{output}\n```", parse_mode="Markdown")

    else:
        await update.message.reply_text("Используйте /start для открытия меню команд")

def main():
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))

    print("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()