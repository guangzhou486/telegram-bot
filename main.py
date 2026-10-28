import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import FastAPI, Request
import uvicorn

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

# ========== Bot 功能（和之前一样） ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"你好 {user.first_name}！👋 发送 /help 查看命令。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 命令：\n/start 开始\n/help 帮助\n/menu 菜单\n/echo <文本> 回声\n/info 用户信息"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"🔊 {' '.join(context.args)}")
    else:
        await update.message.reply_text("⚠️ 请在 /echo 后输入文本")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👤 ID: `{user.id}`\n用户名: @{user.username or '未设置'}",
        parse_mode='Markdown'
    )

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("✅ A", callback_data='a'),
        InlineKeyboardButton("❌ B", callback_data='b')
    ]]
    await update.message.reply_text('请选择：', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"你选了 {'A' if query.data == 'a' else 'B'}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() in ['你好', 'hello', 'hi']:
        await update.message.reply_text("你好！😊")
    else:
        await update.message.reply_text(f"收到：{update.message.text}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("异常:", exc_info=context.error)

# ========== Webhook 服务 ==========

app = FastAPI()
application = None

@app.on_event("startup")
async def startup_event():
    global application
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('echo', echo))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('menu', show_menu))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    await application.initialize()
    await application.start()
    
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook/{TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook 设置成功: {webhook_url}")

@app.post(f"/webhook/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def health():
    return {"status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
