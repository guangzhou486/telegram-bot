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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"你好 {user.first_name}！👋\n"
        "发送 /help 查看所有命令。"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 可用命令：\n\n"
        "/start - 开始使用\n"
        "/help - 显示帮助\n"
        "/menu - 显示菜单\n"
        "/echo <文本> - 回声\n"
        "/info - 用户信息"
    )
    await update.message.reply_text(help_text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"🔊 {' '.join(context.args)}")
    else:
        await update.message.reply_text("⚠️ 请在 /echo 后输入文本")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👤 ID: `{user.id}`\n"
        f"用户名: @{user.username or '未设置'}\n"
        f"名字: {user.first_name}",
        parse_mode='Markdown'
    )


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ 选项 A", callback_data='opt_a'),
            InlineKeyboardButton("❌ 选项 B", callback_data='opt_b')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('请选择：', reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'opt_a':
        await query.edit_message_text(text="✅ 你选择了选项 A")
    elif query.data == 'opt_b':
        await query.edit_message_text(text="❌ 你选择了选项 B")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower() in ['你好', 'hello', 'hi']:
        await update.message.reply_text("你好！😊")
    else:
        await update.message.reply_text(f"收到：{text}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("异常:", exc_info=context.error)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("请设置 TELEGRAM_BOT_TOKEN 环境变量")
    
    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('echo', echo))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('menu', show_menu))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    logger.info("Bot 启动中...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
