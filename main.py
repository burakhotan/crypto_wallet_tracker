import time
import os.path
import re
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler,ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import os
from dotenv import load_dotenv
import wallet_operations
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WALLET_INPUT = 0


# Defining starting message
def start(update, context):
    message = """
👋 Welcome to the *Blast Wallet Tracker*! 🚀

I'm here to help you monitor transactions on Blast Ecosystem. Here's what you can do:

- 📥 *Add Wallet*: Start tracking a new wallet.
- 📤 *List Wallets*: View all wallets you're currently tracking.
- 📤 *Remove Wallet*: Remove a wallet you are tracking.

Just choose an option below to get started. If you ever need help, just type /help.

Let's make some money with insider trading!
    """
    keyboard = [
        [InlineKeyboardButton("Add Wallet", callback_data='add_wallet')],
        [InlineKeyboardButton("List Wallets", callback_data='list_wallets')],
        [InlineKeyboardButton("Remove Wallet", callback_data='remove_wallet')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(message, reply_markup=reply_markup)
    
def button(update, context):
    query = update.callback_query
    query.answer()  # CallbackQueries need to be answered

    if query.data == 'add_wallet':
        query.edit_message_text(text="Please send the wallet address you'd like to add.")
        return WALLET_INPUT
    elif query.data == 'list_wallets':
        # Trigger functionality to list wallets
        query.edit_message_text(text="Listing all watched wallets...")
        list_wallets(update, context)  # Ensure this function can be called here
    else:
        query.edit_message_text(text="Sorry, I didn't understand that.")
    return ConversationHandler.END


def wallet_input(update, context):
    user = update.message.from_user
    wallet_address = update.message.text
    if re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        wallet_operations.add_wallet(wallet_address)
        update.message.reply_text(f'Added {wallet_address} to the list of watched wallets.')
    else:
        update.message.reply_text(f'{wallet_address} is not a valid Ethereum wallet address.')
    return ConversationHandler.END


def add(update, context):
    wallet_address = context.args[0]
    
    # Check if the wallet address is in the correct format for the specified blockchain
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        context.bot.send_message(chat_id=update.message.chat_id, text=f"{wallet_address} is not a valid Ethereum wallet address.")
        return
    
    print(context.args)
    wallet_address = context.args[0]

    wallet_operations.add_wallet(wallet_address)
    message = f'Added {wallet_address} to the list of watched  wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def remove(update, context):
    print(context.args)
    wallet_address = context.args[0]
    print(wallet_address)
    wallet_operations.remove_wallet(wallet_address)
    message = f'Removed {wallet_address} from the list of watched wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)
    
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END
def list_wallets(update, context):
    message = wallet_operations.list_wallets()
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define the command handlers
start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
remove_handler = CommandHandler('remove', remove)
list_handler = CommandHandler('list', list_wallets)
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button)],  # Triggered by pressing the inline button
    states={
        WALLET_INPUT: [MessageHandler(Filters.text & ~Filters.command, wallet_input)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],  # You can add a cancel command to allow users to cancel adding a wallet
)

dispatcher.add_handler(conv_handler)
# Add the command handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(CallbackQueryHandler(button))

# Register the handler for callback queries
button_handler = CallbackQueryHandler(button)
dispatcher.add_handler(button_handler)

updater.start_polling()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram bot started.")

print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring wallets...")
wallet_operations.monitor_wallets()