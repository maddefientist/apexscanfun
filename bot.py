import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, ConversationHandler, MessageHandler, filters
)

from config import TELEGRAM_TOKEN, TIMEFRAMES, DEFAULT_TIMEFRAME
from data_fetcher import get_token_chart_data, get_token_metadata
from legend import LEGEND_TEXT

logger = logging.getLogger(__name__)

TIMEFRAME = 0
TIMEFRAME_PREFIX = "tf_"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 *Welcome to SPL Token Chart Bot!*\n\n"
        "I can generate technical analysis charts for any SPL token on Solana.\n\n"
        "*Commands:*\n"
        "• `/chart <token_address>` - Generate a chart with indicators\n"
        "• `/legend` - Explain chart indicators\n"
        "• `/help` - Show this help message\n\n"
        "Example: `/chart 9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E`"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def legend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(LEGEND_TEXT, parse_mode='Markdown')

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide a token address. Example:\n"
            "`/chart 9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E`",
            parse_mode='Markdown'
        )
        return
    
    token_address = context.args[0]
    timeframe = DEFAULT_TIMEFRAME
    if len(context.args) > 1 and context.args[1] in TIMEFRAMES:
        timeframe = context.args[1]
    
    context.user_data['token_address'] = token_address
    
    keyboard = []
    row = []
    for tf, tf_data in TIMEFRAMES.items():
        text = f"✓ {tf_data['name']}" if tf == timeframe else tf_data['name']
        row.append(InlineKeyboardButton(text, callback_data=f"{TIMEFRAME_PREFIX}{tf}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    processing_message = await update.message.reply_text(
        f"📊 Fetching chart for {token_address}...\n"
        f"Timeframe: {TIMEFRAMES[timeframe]['name']}",
        reply_markup=reply_markup
    )
    
    context.user_data['message_id'] = processing_message.message_id
    
    await generate_and_send_chart(update, context, token_address, timeframe)

async def timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle timeframe selection callbacks."""
    query = update.callback_query
    await query.answer()
    
    timeframe = query.data.replace(TIMEFRAME_PREFIX, "")
    
    token_address = context.user_data.get('token_address')
    if not token_address:
        await query.edit_message_text("Session expired. Please use /chart command again.")
        return
    
    await query.edit_message_text(
        f"📊 Updating chart for {token_address}...\n"
        f"Timeframe: {TIMEFRAMES[timeframe]['name']}",
        reply_markup=query.message.reply_markup
    )
    
    await generate_and_send_chart(update, context, token_address, timeframe, is_callback=True)

async def generate_and_send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  token_address: str, timeframe: str, is_callback: bool = False):
    """Generate and send a chart with the given parameters."""
    try:
        img_path, analysis_text = get_token_chart_data(token_address, timeframe)
        
        if img_path and analysis_text:
            chat_id = update.effective_chat.id
            
            with open(img_path, 'rb') as photo:
                if is_callback:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=analysis_text,
                        parse_mode='Markdown'
                    )
                else:
                    message_id = context.user_data.get('message_id')
                    if message_id:
                        await context.bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=message_id,
                            media=InputMediaPhoto(media=photo)
                        )
                        await context.bot.edit_message_caption(
                            chat_id=chat_id,
                            message_id=message_id,
                            caption=analysis_text,
                            parse_mode='Markdown'
                        )
                    else:
                        await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=analysis_text,
                            parse_mode='Markdown'
                        )
        else:
            await update.message.reply_text("Failed to generate chart.")
    except Exception as e:
        logger.error(f"Error generating/sending chart: {e}")
        await update.message.reply_text("An error occurred while generating the chart.")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("legend", legend))
    application.add_handler(CommandHandler("chart", chart))
    application.add_handler(CallbackQueryHandler(timeframe_callback, pattern=f"^{TIMEFRAME_PREFIX}"))

    # Run the bot until the user presses Ctrl-C
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    import asyncio
    import sys
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # If this error still occurs, re-raise it
        raise
