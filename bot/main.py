import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import sys
import os
from PIL import Image, ImageDraw, ImageFilter
import io

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import BOT_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your Polaroid bot! Send me a photo and I will convert it to a polaroid style!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('📸 Send me a photo and I will convert it to a polaroid style!\n\nJust send any image and I\'ll add a classic polaroid frame and effect.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send a processing message
        processing_msg = await update.message.reply_text("🎨 Processing your photo...")
        
        # Get the largest photo (highest quality)
        photo = update.message.photo[-1]
        
        # Download the photo
        file = await photo.get_file()
        
        # Download to memory
        photo_bytes = await file.download_as_bytearray()
        
        # Open image with PIL
        img = Image.open(io.BytesIO(photo_bytes))
        
        # Convert to polaroid style
        polaroid_img = create_polaroid(img)
        
        # Save to memory
        output = io.BytesIO()
        polaroid_img.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        # Send back the processed photo
        await update.message.reply_photo(
            photo=output,
            caption="📸 Here's your polaroid photo! 🖼️"
        )
        
        # Delete the processing message
        await processing_msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"Sorry, an error occurred: {str(e)}")

def create_polaroid(img):
    """Convert image to polaroid style"""
    # Resize image to fit polaroid frame
    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
    
    # Define polaroid frame dimensions
    padding = 40  # White border
    bottom_padding = 80  # Extra space at bottom for classic polaroid look
    
    # Create new image with white background
    polaroid = Image.new('RGB', 
                         (img.width + padding * 2, 
                          img.height + padding + bottom_padding), 
                         'white')
    
    # Paste original image
    polaroid.paste(img, (padding, padding))
    
    # Optional: Add a shadow effect
    draw = ImageDraw.Draw(polaroid)
    
    # Add a subtle shadow at the bottom
    shadow_height = 20
    for i in range(shadow_height):
        alpha = int(50 * (1 - i/shadow_height))
        draw.rectangle(
            [(0, polaroid.height - shadow_height + i), 
             (polaroid.width, polaroid.height - shadow_height + i + 1)],
            fill=(200, 200, 200, alpha)
        )
    
    return polaroid

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Start the bot
    print("Bot is starting...")
    print("Send your bot a photo to convert it to polaroid style!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()