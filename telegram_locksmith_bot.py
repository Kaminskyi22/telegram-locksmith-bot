import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = "7758144538:AAFpz2aBdNLK3vA-jYEU_S1cloVgDtHTC80"  # Ваш токен
ADMIN_CHAT_ID = "6125664936"  # Ваш Chat ID
PORT = int(os.environ.get('PORT', 8443))

# Перевірка наявності змінних середовища
if not ADMIN_CHAT_ID:
    logger.error("ADMIN_CHAT_ID не встановлено! Будь ласка, встановіть змінну середовища ADMIN_CHAT_ID.")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f'Привіт {user.first_name}! Я бот-помічник. Надішліть мені повідомлення, фото або локацію, і я передам їх адміністратору.'
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
    if location:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f'Локація від {user.first_name} (ID: {user.id}):\nШирота: {location.latitude}\nДовгота: {location.longitude}'
        )
        await context.bot.send_location(
            chat_id=ADMIN_CHAT_ID,
            latitude=location.latitude,
            longitude=location.longitude
        )
        await update.message.reply_text('Ваша локація отримана та передана адміністратору.')
    else:
        await update.message.reply_text('Не вдалося отримати локацію.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos."""
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f'Фото від {user.first_name} (ID: {user.id})'
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=caption
    )
    await update.message.reply_text('Ваше фото отримано та передано адміністратору.')

def main() -> None:
    """Start the bot."""
    try:
        # Create the Application and pass it your bot's token
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.LOCATION, handle_location))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        # Start the Bot with webhook configuration
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"https://telegram-locksmith-bot.onrender.com/{BOT_TOKEN}",
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"Помилка запуску бота: {str(e)}")
        raise

if __name__ == '__main__':
    main() 