import os
import shutil
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image
import ffmpeg
import PyPDF2

# --- Get BOT_TOKEN from environment ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables!")
    print("📝 Please add BOT_TOKEN (or TOKEN) to Railway Variables")
    exit(1)

print("✅ BOT_TOKEN found! Starting bot...")

# --- Supported Formats ---
SUPPORTED_IMAGE_FORMATS = {
    "jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP",
    "bmp": "BMP", "tiff": "TIFF", "ico": "ICO", "gif": "GIF"
}

SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mkv", "mov", "webm", "flv", "3gp"]
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma"]
SUPPORTED_DOC_FORMATS = ["pdf", "txt", "csv", "json", "xml", "html"]

# --- Helper Functions ---

def get_file_extension(file_name):
    return Path(file_name).suffix.lower()

def is_image(filename):
    ext = get_file_extension(filename)
    return ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".ico", ".gif"]

def is_video(filename):
    ext = get_file_extension(filename)
    return ext in [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv", ".3gp"]

def is_audio(filename):
    ext = get_file_extension(filename)
    return ext in [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"]

def is_document(filename):
    ext = get_file_extension(filename)
    return ext in [".pdf", ".txt", ".csv", ".json", ".xml", ".html"]

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    keyboard = [[InlineKeyboardButton("📚 Help", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 *Welcome to File Converter Bot!*\n\n"
        f"I can convert your files between different formats.\n\n"
        f"📸 *Images:* {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}\n"
        f"🎬 *Videos:* {', '.join(SUPPORTED_VIDEO_FORMATS)}\n"
        f"🎵 *Audio:* {', '.join(SUPPORTED_AUDIO_FORMATS)}\n"
        f"📄 *Documents:* {', '.join(SUPPORTED_DOC_FORMATS)}\n\n"
        f"*How to use:*\n"
        f"1️⃣ Send me a file\n"
        f"2️⃣ In the caption, specify the output format\n"
        f"3️⃣ Example: Send a PNG with caption 'jpg'\n\n"
        f"Use /help for more information.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    keyboard = [[InlineKeyboardButton("🏠 Home", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🛠 *How to use me:*\n\n"
        f"1. Send any file (image, video, audio, document)\n"
        f"2. Add the target format in the caption\n"
        f"3. Wait for the converted file\n\n"
        f"*Examples:*\n"
        f"📸 Send a PNG image with caption 'jpg' → converts to JPG\n"
        f"🎬 Send an AVI video with caption 'mp4' → converts to MP4\n"
        f"🎵 Send an OGG audio with caption 'mp3' → converts to MP3\n\n"
        f"*Supported formats:*\n"
        f"Images: {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}\n"
        f"Videos: {', '.join(SUPPORTED_VIDEO_FORMATS)}\n"
        f"Audio: {', '.join(SUPPORTED_AUDIO_FORMATS)}\n"
        f"Documents: {', '.join(SUPPORTED_DOC_FORMATS)}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start":
        keyboard = [[InlineKeyboardButton("📚 Help", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"👋 *Welcome to File Converter Bot!*\n\n"
            f"I can convert your files between different formats.\n\n"
            f"📸 *Images:* {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}\n"
            f"🎬 *Videos:* {', '.join(SUPPORTED_VIDEO_FORMATS)}\n"
            f"🎵 *Audio:* {', '.join(SUPPORTED_AUDIO_FORMATS)}\n"
            f"📄 *Documents:* {', '.join(SUPPORTED_DOC_FORMATS)}\n\n"
            f"*How to use:*\n"
            f"1️⃣ Send me a file\n"
            f"2️⃣ In the caption, specify the output format\n"
            f"3️⃣ Example: Send a PNG with caption 'jpg'\n\n"
            f"Use /help for more information.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif query.data == "help":
        keyboard = [[InlineKeyboardButton("🏠 Home", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🛠 *How to use me:*\n\n"
            f"1. Send any file (image, video, audio, document)\n"
            f"2. Add the target format in the caption\n"
            f"3. Wait for the converted file\n\n"
            f"*Examples:*\n"
            f"📸 Send a PNG image with caption 'jpg' → converts to JPG\n"
            f"🎬 Send an AVI video with caption 'mp4' → converts to MP4\n"
            f"🎵 Send an OGG audio with caption 'mp3' → converts to MP3\n\n"
            f"*Supported formats:*\n"
            f"Images: {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}\n"
            f"Videos: {', '.join(SUPPORTED_VIDEO_FORMATS)}\n"
            f"Audio: {', '.join(SUPPORTED_AUDIO_FORMATS)}\n"
            f"Documents: {', '.join(SUPPORTED_DOC_FORMATS)}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# --- File Conversion Functions ---

async def convert_image(file_path, output_format):
    """Convert image to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        img = Image.open(file_path)
        
        if output_format.lower() in ["jpg", "jpeg"]:
            img = img.convert("RGB")
        
        if output_format.lower() == "ico":
            img.save(output_path, format="ICO", sizes=[(256, 256)])
        else:
            img.save(output_path, format=SUPPORTED_IMAGE_FORMATS.get(output_format, output_format.upper()))
        
        return str(output_path)
    except Exception as e:
        print(f"Image conversion error: {e}")
        return None

async def convert_video(file_path, output_format):
    """Convert video to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        ffmpeg.input(file_path).output(
            str(output_path),
            acodec='aac' if output_format in ['mp4', 'webm', 'mkv'] else 'copy',
            vcodec='libx264' if output_format == 'mp4' else 'copy'
        ).run(quiet=True, overwrite_output=True)
        return str(output_path)
    except Exception as e:
        print(f"Video conversion error: {e}")
        return None

async def convert_audio(file_path, output_format):
    """Convert audio to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        ffmpeg.input(file_path).output(str(output_path)).run(quiet=True, overwrite_output=True)
        return str(output_path)
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return None

async def convert_document(file_path, output_format):
    """Convert document to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        
        if output_format == "txt" and file_path.endswith(".pdf"):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(text)
            return str(output_path)
        else:
            shutil.copy2(file_path, output_path)
            return str(output_path)
    except Exception as e:
        print(f"Document conversion error: {e}")
        return None

# --- File Handler ---

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file conversion."""
    try:
        message = update.message
        document = message.document or message.photo or message.video or message.audio
        
        if not document:
            await message.reply_text("❌ Please send a valid file.")
            return
        
        # Get output format from caption
        if not message.caption:
            await message.reply_text(
                "📎 Please add the output format in the caption.\n"
                "Example: Send this file with caption 'jpg' to convert it.\n"
                "Use /help to see supported formats."
            )
            return
        
        output_format = message.caption.lower().strip()
        
        # Download file
        status_msg = await message.reply_text("🔄 *Processing your file...*\nPlease wait.", parse_mode='Markdown')
        
        # Get file
        if message.photo:
            file = await message.photo[-1].get_file()
        elif message.document:
            file = await message.document.get_file()
        elif message.video:
            file = await message.video.get_file()
        elif message.audio:
            file = await message.audio.get_file()
        else:
            await status_msg.edit_text("❌ Unsupported file type.")
            return
        
        file_path = f"download_{file.file_id}"
        await file.download_to_drive(file_path)
        
        # Determine file type and convert
        if is_image(file_path):
            if output_format not in SUPPORTED_IMAGE_FORMATS:
                await status_msg.edit_text(
                    f"❌ Format not supported for images.\n"
                    f"Supported: {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}"
                )
                os.remove(file_path)
                return
            
            output_file = await convert_image(file_path, output_format)
            if output_file:
                with open(output_file, 'rb') as f:
                    await message.reply_document(
                        document=f,
                        caption=f"✅ *Converted to {output_format.upper()}*",
                        parse_mode='Markdown'
                    )
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        elif is_video(file_path):
            if output_format not in SUPPORTED_VIDEO_FORMATS:
                await status_msg.edit_text(
                    f"❌ Format not supported for videos.\n"
                    f"Supported: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
                )
                os.remove(file_path)
                return
            
            output_file = await convert_video(file_path, output_format)
            if output_file:
                with open(output_file, 'rb') as f:
                    await message.reply_video(
                        video=f,
                        caption=f"✅ *Converted to {output_format.upper()}*",
                        parse_mode='Markdown'
                    )
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        elif is_audio(file_path):
            if output_format not in SUPPORTED_AUDIO_FORMATS:
                await status_msg.edit_text(
                    f"❌ Format not supported for audio.\n"
                    f"Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
                )
                os.remove(file_path)
                return
            
            output_file = await convert_audio(file_path, output_format)
            if output_file:
                with open(output_file, 'rb') as f:
                    await message.reply_audio(
                        audio=f,
                        caption=f"✅ *Converted to {output_format.upper()}*",
                        parse_mode='Markdown'
                    )
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        elif is_document(file_path):
            if output_format not in SUPPORTED_DOC_FORMATS:
                await status_msg.edit_text(
                    f"❌ Format not supported for documents.\n"
                    f"Supported: {', '.join(SUPPORTED_DOC_FORMATS)}"
                )
                os.remove(file_path)
                return
            
            output_file = await convert_document(file_path, output_format)
            if output_file:
                with open(output_file, 'rb') as f:
                    await message.reply_document(
                        document=f,
                        caption=f"✅ *Converted to {output_format.upper()}*",
                        parse_mode='Markdown'
                    )
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        else:
            await status_msg.edit_text(
                "❌ Unsupported file type.\n"
                f"Supported: Images, Videos, Audio, Documents"
            )
            os.remove(file_path)
            
    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages without file."""
    await update.message.reply_text(
        "🤔 Please send a file with the desired format in the caption.\n"
        "Example: Send an image with caption 'jpg' to convert to JPG.\n"
        "Use /help for more information."
    )

# --- Main Function ---

def main():
    """Start the bot."""
    print("🚀 Starting File Converter Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, 
        handle_file
    ))
    
    # Start bot
    print("✅ Bot is running! Waiting for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
