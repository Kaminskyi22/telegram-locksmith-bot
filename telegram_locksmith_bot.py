import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
PORT = int(os.environ.get('PORT', 8443))
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

# Логування змінних середовища (без токена)
logger.info(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
logger.info(f"PORT: {PORT}")
logger.info(f"RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME}")

# Перевірка наявності змінних середовища
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не встановлено!")
    exit(1)
if not ADMIN_CHAT_ID:
    logger.error("ADMIN_CHAT_ID не встановлено!")
    exit(1)
if not RENDER_EXTERNAL_HOSTNAME:
    logger.error("RENDER_EXTERNAL_HOSTNAME не встановлено!")
    exit(1)

# Клавіатура з кнопками
keyboard = [
    [KeyboardButton("📍 Передати локацію", request_location=True)],
    [KeyboardButton("🖼️ Передати зображення")],
    [KeyboardButton("🎤 Надіслати голосове")],
    [KeyboardButton("🎥 Відео кружечок")],
    [KeyboardButton("📞 Зателефонувати", request_contact=True)],
    [KeyboardButton("ℹ️ Інформація"), KeyboardButton("📝 Залишити відгук")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"start() called by user: {user.id} ({user.first_name})")
    await update.message.reply_text(
        f'Привіт {user.first_name}! Я бот-помічник. Оберіть дію нижче:',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user = update.effective_user
    message = update.message.text
    logger.info(f"handle_message() called by user: {user.id} ({user.first_name}), message: {message}")
    
    # Обробка кнопок
    if message == "ℹ️ Інформація":
        await update.message.reply_text("Я бот для зв'язку з адміністратором. Ви можете передати локацію, фото, голосове, відео-кружечок або написати повідомлення.")
        return
    elif message == "📝 Залишити відгук":
        await update.message.reply_text("Напишіть ваш відгук у відповідь на це повідомлення.")
        return
    elif message == "📞 Зателефонувати":
        await update.message.reply_text("Телефонуйте за номером: +380XXXXXXXXX")
        return
    elif message == "🖼️ Передати зображення":
        await update.message.reply_text("Будь ласка, надішліть фото у чат.")
        return
    elif message == "🎤 Надіслати голосове":
        await update.message.reply_text("Будь ласка, надішліть голосове повідомлення у чат.")
        return
    elif message == "🎥 Відео кружечок":
        await update.message.reply_text("Будь ласка, надішліть відео-кружечок у чат.")
        return

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
    logger.info(f"handle_location() called by user: {user.id} ({user.first_name}), location: {location}")
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
    logger.info(f"handle_photo() called by user: {user.id} ({user.first_name})")
    photo = update.message.photo[-1]
    caption = f'Фото від {user.first_name} (ID: {user.id})'
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=caption
    )
    await update.message.reply_text('Ваше фото отримано та передано адміністратору.')

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"handle_voice() called by user: {user.id} ({user.first_name})")
    voice = update.message.voice
    await context.bot.send_voice(
        chat_id=ADMIN_CHAT_ID,
        voice=voice.file_id,
        caption=f'Голосове від {user.first_name} (ID: {user.id})'
    )
    await update.message.reply_text('Ваше голосове повідомлення передано адміністратору.')

async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"handle_video_note() called by user: {user.id} ({user.first_name})")
    video_note = update.message.video_note
    await context.bot.send_video_note(
        chat_id=ADMIN_CHAT_ID,
        video_note=video_note.file_id
    )
    await update.message.reply_text('Ваше відео-кружечок передано адміністратору.')

async def webhook_handler(request):
    """Handle incoming webhook updates."""
    try:
        application = request.app['application']
        data = await request.json()
        logger.info(f"Received webhook update: {data}")
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}")
        return web.Response(status=500, text=str(e))

async def main():
    """Start the bot."""
    try:
        # Create the Application and pass it your bot's token
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.LOCATION, handle_location))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))

        # Delete any existing webhook
        await application.bot.delete_webhook()
        logger.info("Deleted existing webhook")

        # Set up webhook
        webhook_path = f"/webhook/{BOT_TOKEN}"
        webhook_url = f"https://{RENDER_EXTERNAL_HOSTNAME}{webhook_path}"
        logger.info(f"Setting up webhook at: {webhook_url}")
        
        await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"]
        )
        logger.info("Webhook set successfully")

        # Set up aiohttp server
        app = web.Application()
        app['application'] = application
        app.router.add_post(webhook_path, webhook_handler)
        
        # Add health check endpoint
        async def health_check(request):
            return web.Response(text="OK")
        
        app.router.add_get("/health", health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Server started on port {PORT}")

        # Keep the application running
        await asyncio.Event().wait()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main()) 