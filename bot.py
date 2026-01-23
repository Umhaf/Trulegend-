import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, db

# --- 1. CONFIGURATION ---
BOT_TOKEN = '8398377608:AAFz-1BO20B325T5e4TrYXJPxwrwWpWruAI'
MINI_APP_URL = 'https://trulegendbot.netlify.app'
CERT_PATH = "/home/Legend130/serviceAccountKey.json"

# --- 2. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CERT_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://trulegend-be32e-default-rtdb.firebaseio.com'
        })
        print("✅ Firebase Connected Successfully")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")

# --- 3. BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  # This is where the referral ID comes from (?start=12345)
    
    user_ref = db.reference(f'users/{user.id}')
    user_data = user_ref.get()

    # REFERRAL SYSTEM LOGIC
    if not user_data and args:
        referrer_id = args[0]
        
        # 1. Check if the referrer is NOT the user themselves
        # 2. Check if the referrer actually exists in our database
        if referrer_id != str(user.id):
            ref_path = db.reference(f'users/{referrer_id}')
            referrer_data = ref_path.get()
            
            if referrer_data:
                # Add the bonus to the referrer
                new_balance = referrer_data.get('balance', 0) + 25000
                new_ref_count = referrer_data.get('referrals', 0) + 1
                
                ref_path.update({
                    'balance': new_balance,
                    'referrals': new_ref_count
                })
                
                # Notify the referrer that they got money!
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id, 
                        text=f"🎁 **Referral Bonus!**\n\n{user.first_name} joined using your link. You earned **+25,000 $TRU**!",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Could not message referrer {referrer_id}: {e}")
            else:
                print(f"Referral link used, but ID {referrer_id} not found in Database.")

    # CREATE NEW USER IF THEY DON'T EXIST
    if not user_data:
        user_ref.set({
            'id': user.id,
            'username': user.first_name,
            'balance': 0,
            'energy': 1000,
            'referrals': 0,
            'streak': 0,
            'lastDaily': 0,
            'completedTasks': []
        })
        print(f"🆕 New User Created: {user.first_name} ({user.id})")

    # REPLY KEYBOARD
    keyboard = [[InlineKeyboardButton("🎮 PLAY TRULEGEND", web_app=WebAppInfo(url=MINI_APP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome to **TRULEGEND PRO**, {user.first_name}! 💎\n\n"
        "Mine $TRU, complete missions, and climb the leaderboard.\n\n"
        "🚀 **Next Airdrop Drop:** Q2 2026",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("🚀 Bot is LIVE and listening for users...")
    application.run_polling()

if __name__ == '__main__':
    main()