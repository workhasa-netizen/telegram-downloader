import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = '8678364203:AAGjYz1anxA47r1pmiW_7IsBL6a8RGm4u2c'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي أي رابط من (إكس، إنستغرام، أو تيك توك) وسأقوم بتحميل الفيديو أو الصور فوراً وبدون حدود أو إعلانات.")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.effective_chat.id
    
    if not url or not url.startswith('http'):
        return

    msg = await update.message.reply_text("⏳ جاري تحليل الرابط وتحميل المحتوى...")

    downloaded_files = []
    
    ydl_opts = {
        'outtmpl': f'media_{chat_id}_%(id)s_%(autonumber)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            entries = info['entries'] if 'entries' in info else [info]

            for entry in entries:
                filename = ydl.prepare_filename(entry)
                if os.path.exists(filename):
                    downloaded_files.append(filename)

        if not downloaded_files:
            await msg.edit_text("❌ لم يتم العثور على محتوى قابل للتحميل.")
            return

        await msg.edit_text("📤 جاري إرسال المحتوى إلى تلغرام...")

        photos = []
        for file_path in downloaded_files:
            ext = file_path.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                photos.append(open(file_path, 'rb'))
            elif ext in ['mp4', 'mkv', 'webm', 'mov']:
                with open(file_path, 'rb') as video_file:
                    await context.bot.send_video(chat_id=chat_id, video=video_file)

        if photos:
            if len(photos) == 1:
                await context.bot.send_photo(chat_id=chat_id, photo=photos[0])
            else:
                media_group = [InputMediaPhoto(p) for p in photos[:10]]
                await context.bot.send_media_group(chat_id=chat_id, media=media_group)

            for p in photos:
                p.close()

        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط وأن الحساب عام وليس خاصاً.")
        
    finally:
        for file_path in downloaded_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()