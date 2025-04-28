import os
import telegram

# Print current environment variables
print("Environment Variables:")
print(f"OKX_API_KEY: {'***' + os.environ.get('OKX_API_KEY', '')[-4:] if os.environ.get('OKX_API_KEY') else 'YOK'}")
print(f"OKX_API_SECRET: {'***' + os.environ.get('OKX_API_SECRET', '')[-4:] if os.environ.get('OKX_API_SECRET') else 'YOK'}")
print(f"TELEGRAM_BOT_TOKEN: {'***' + os.environ.get('TELEGRAM_BOT_TOKEN', '')[-4:] if os.environ.get('TELEGRAM_BOT_TOKEN') else 'YOK'}")
print(f"TELEGRAM_CHAT_ID: {os.environ.get('TELEGRAM_CHAT_ID', 'YOK')}")

# Try Telegram bot connection
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
if token:
    try:
        bot = telegram.Bot(token=token)
        me = bot.get_me()
        print(f"\nTelegram Bot Connection: SUCCESS")
        print(f"Bot Name: {me.first_name}")
        print(f"Bot Username: @{me.username}")
    except Exception as e:
        print(f"\nTelegram Bot Connection: FAILED")
        print(f"Error: {e}")
else:
    print("\nTelegram Bot Token is not defined!")
