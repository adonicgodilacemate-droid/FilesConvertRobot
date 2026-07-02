import os
import sys
import shutil
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from PIL import Image
import ffmpeg
import PyPDF2

# --- DEBUG: Print all environment variables (for debugging only) ---
print("=" * 50)
print("🔍 Checking Environment Variables:")
print("=" * 50)

# Try both naming conventions
API_ID = os.environ.get("API_ID") or os.environ.get("ID")
API_HASH = os.environ.get("API_HASH") or os.environ.get("HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TOKEN")

# Print what we found (masked for security)
print(f"✅ API_ID: {'✅ Found' if API_ID else '❌ Missing'}")
print(f"✅ API_HASH: {'✅ Found' if API_HASH else '❌ Missing'}")
print(f"✅ BOT_TOKEN: {'✅ Found' if BOT_TOKEN else '❌ Missing'}")

if API_ID:
    print(f"📊 API_ID length: {len(str(API_ID))} characters")
if API_HASH:
    print(f"📊 API_HASH length: {len(API_HASH)} characters")
if BOT_TOKEN:
    print(f"📊 BOT_TOKEN length: {len(BOT_TOKEN)} characters")

print("=" * 50)

# --- Validate Configuration ---
missing_vars = []
if not API_ID:
    missing_vars.append("API_ID or ID")
if not API_HASH:
    missing_vars.append("API_HASH or HASH")
if not BOT_TOKEN:
    missing_vars.append("BOT_TOKEN or TOKEN")

if missing_vars:
    error_msg = (
        f"\n❌ MISSING ENVIRONMENT VARIABLES:\n"
        f"   {', '.join(missing_vars)}\n\n"
        f"📝 How to fix:\n"
        f"   1. Go to Railway Dashboard → Your Project → Variables\n"
        f"   2. Add these variables:\n"
        f"      - API_ID (or ID) = Your numeric API ID\n"
        f"      - API_HASH (or HASH) = Your API Hash\n"
        f"      - BOT_TOKEN (or TOKEN) = Your Bot Token\n"
        f"   3. Click 'Redeploy'\n\n"
        f"🔗 Get your credentials:\n"
        f"   - API_ID/HASH: https://my.telegram.org/apps\n"
        f"   - BOT_TOKEN: @BotFather on Telegram\n"
    )
    print(error_msg)
    sys.exit(1)

# Convert API_ID to int
try:
    API_ID = int(API_ID)
    print(f"✅ API_ID converted to int: {API_ID}")
except ValueError:
    print(f"❌ API_ID must be a number, got: {API_ID}")
    sys.exit(1)

print("✅ All environment variables are set correctly!")
print("=" * 50)

# --- Initialize Bot ---
app = Client(
    "file_converter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

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
    """Extract file extension from filename."""
    return Path(file_name).suffix.lower()

def is_image(filename):
    """Check if file is an image."""
    ext = get_file_extension(filename)
    return ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".ico", ".gif"]

def is_video(filename):
    """Check if file is a video."""
    ext = get_file_extension(filename)
    return ext in [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv", ".3gp"]

def is_audio(filename):
    """Check if file is an audio."""
    ext = get_file_extension(filename)
    return ext in [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"]

def is_document(filename):
    """Check if file is a document."""
    ext = get_file_extension(filename)
    return ext in [".pdf", ".txt", ".csv", ".json", ".xml", ".html"]

# --- Bot Command Handlers ---

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    """Handle /start command."""
    await message.reply_text(
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
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Help", callback_data="help")]
        ])
    )

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    """Handle /help command."""
    await message.reply_text(
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
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ])
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    """Handle inline button callbacks."""
    data = callback_query.data
    if data == "start":
        await start_command(client, callback_query.message)
    elif data == "help":
        await help_command(client, callback_query.message)
    await callback_query.answer()

# --- File Conversion Handlers ---

@app.on_message(filters.document | filters.photo | filters.video | filters.audio & filters.caption)
async def handle_file_conversion(client, message: Message):
    """Main handler for file conversion."""
    try:
        # Extract output format from caption
        output_format = message.caption.lower().strip()
        
        # Download the file
        status_msg = await message.reply_text("🔄 *Processing your file...*\nPlease wait.")
        
        file_path = await client.download_media(message)
        if not file_path:
            await status_msg.edit_text("❌ Failed to download the file.")
            return
        
        # Determine file type and convert
        original_filename = Path(file_path).name
        
        # --- Image Conversion ---
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
                await send_converted_file(client, message, output_file, "image", output_format)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            # Cleanup
            os.remove(file_path)
            await status_msg.delete()
        
        # --- Video Conversion ---
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
                await send_converted_file(client, message, output_file, "video", output_format)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        # --- Audio Conversion ---
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
                await send_converted_file(client, message, output_file, "audio", output_format)
            else:
                await status_msg.edit_text("❌ Conversion failed. Please try again.")
            
            os.remove(file_path)
            await status_msg.delete()
        
        # --- Document Conversion ---
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
                await send_converted_file(client, message, output_file, "document", output_format)
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

# --- Conversion Functions ---

async def convert_image(file_path, output_format):
    """Convert image to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        img = Image.open(file_path)
        
        # Handle special cases
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
        
        # Use ffmpeg for video conversion
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
        
        # Use ffmpeg for audio conversion
        ffmpeg.input(file_path).output(str(output_path)).run(quiet=True, overwrite_output=True)
        
        return str(output_path)
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return None

async def convert_document(file_path, output_format):
    """Convert document to specified format."""
    try:
        output_path = Path(file_path).with_suffix(f".{output_format}")
        
        # Simple document conversion (you can expand this)
        if output_format == "txt" and file_path.endswith(".pdf"):
            # Extract text from PDF
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(text)
            
            return str(output_path)
        else:
            # For other formats, just copy the file with new extension
            shutil.copy2(file_path, output_path)
            return str(output_path)
            
    except Exception as e:
        print(f"Document conversion error: {e}")
        return None

# --- Helper to Send Converted File ---

async def send_converted_file(client, message, file_path, file_type, format_name):
    """Send the converted file back to the user."""
    try:
        # Determine the appropriate send method
        if file_type == "image":
            await client.send_photo(
                chat_id=message.chat.id,
                photo=file_path,
                caption=f"✅ *Converted to {format_name.upper()}*"
            )
        elif file_type == "video":
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=f"✅ *Converted to {format_name.upper()}*"
            )
        elif file_type == "audio":
            await client.send_audio(
                chat_id=message.chat.id,
                audio=file_path,
                caption=f"✅ *Converted to {format_name.upper()}*"
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"✅ *Converted to {format_name.upper()}*"
            )
        
        # Cleanup output file
        os.remove(file_path)
        
    except Exception as e:
        print(f"Error sending file: {e}")

# --- Fallback Handler ---

@app.on_message(filters.text & ~filters.command)
async def text_handler(client, message: Message):
    """Handle text messages without file."""
    await message.reply_text(
        "🤔 Please send a file with the desired format in the caption.\n"
        "Example: Send an image with caption 'jpg' to convert to JPG.\n"
        "Use /help for more information."
    )

@app.on_message(filters.document | filters.photo | filters.video | filters.audio)
async def file_without_caption(client, message: Message):
    """Handle files sent without caption."""
    await message.reply_text(
        "📎 I received your file!\n"
        "Please add the output format in the caption.\n"
        "Example: Send this file with caption 'jpg' to convert it.\n"
        "Use /help to see supported formats."
    )

# --- Main Function ---

if __name__ == "__main__":
    print("🚀 Bot is starting...")
    print("✨ Bot is ready to convert files!")
    print("=" * 50)
    app.run()
