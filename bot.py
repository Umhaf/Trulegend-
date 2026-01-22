import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, db

# 1. FIREBASE SETUP
# Download your serviceAccountKey.json from Firebase Console -> Project Settings -> Service Accounts
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trulegend-be32e-default-rtdb.firebaseio.com'
})

# 2. BOT CONFIG
'8398377608:AAFz-1BO20B325T5e4TrYXJPxwrwWpWruAI'
MINI_APP_URL = 'https://trulegendbot.netlify.app' # The link to your hosted HTML file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  # This captures the 'start=ID' part
    
    user_ref = db.reference(f'users/{user.id}')
    user_data = user_ref.get()

    # IF NEW USER (Referral Logic)
    if not user_data and args:
        referrer_id = args[0]
        if referrer_id != str(user.id):  # Prevent self-referral
            ref_path = db.reference(f'users/{referrer_id}')
            referrer_data = ref_path.get()
            
            if referrer_data:
                # Add 25k to the person who invited them
                new_balance = referrer_data.get('balance', 0) + 25000
                new_ref_count = referrer_data.get('referrals', 0) + 1
                ref_path.update({
                    'balance': new_balance,
                    'referrals': new_ref_count
                })
                # Notify the referrer (Optional)
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id, 
                        text=f"🎁 Someone joined using your link! You earned +25,000 $TRU"
                    )
                except: pass

    # Initialize user in DB if they don't exist
    if not user_data:
        user_ref.set({
            'id': user.id,
            'username': user.first_name,
            'balance': 0,
            'energy': 1000,
            'referrals': 0,
            'streak': 0,
            'lastDaily': 0
        })

    # Keyboard with Mini App button
    keyboard = [[InlineKeyboardButton("🎮 PLAY TRULEGEND", web_app=WebAppInfo(url=MINI_APP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Hi {user.first_name}! Welcome to **TRULEGEND**.\n\n"
        "Mine $TRU coins, complete tasks, and prepare for the Airdrop.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()