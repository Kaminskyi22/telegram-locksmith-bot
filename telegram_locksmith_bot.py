import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = "7758144538:AAGNt0BbK-SDGgTeMo1IUFh0eE2tMTEoQt4"  # Ваш токен
ADMIN_CHAT_ID = "6125664936"  # Ваш Chat ID

# Перевірка наявності змінних середовища
if not ADMIN_CHAT_ID:
    logger.error("ADMIN_CHAT_ID не встановлено! Будь ласка, встановіть змінну середовища ADMIN_CHAT_ID.")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f'Привіт {user.first_name}! Я бот-помічник. Надішліть мені повідомлення або локацію, і я передам їх адміністратору.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user = update.effective_user
    message = update.message.text
    
    # Forward message to admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f'Нове повідомлення від {user.first_name} (ID: {user.id}):\n\n{message}'
    )
    
    # Send confirmation to user
    await update.message.reply_text('Ваше повідомлення отримано та передано адміністратору.')

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming location."""
    user = update.effective_user
    location = update.message.location
    
    # Forward location to admin
    await context.bot.send_location(
        chat_id=ADMIN_CHAT_ID,
        latitude=location.latitude,
        longitude=location.longitude,
        caption=f'Локація від {user.first_name} (ID: {user.id})'
    )
    
    # Send confirmation to user
    await update.message.reply_text('Ваша локація отримана та передана адміністратору.')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 