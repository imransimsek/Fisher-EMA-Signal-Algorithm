import os
import telegram

# Mevcut ortam değişkenlerini yazdır
print("Ortam Değişkenleri:")
print(f"OKX_API_KEY: {'***' + os.environ.get('OKX_API_KEY', '')[-4:] if os.environ.get('OKX_API_KEY') else 'YOK'}")
print(f"OKX_API_SECRET: {'***' + os.environ.get('OKX_API_SECRET', '')[-4:] if os.environ.get('OKX_API_SECRET') else 'YOK'}")
print(f"TELEGRAM_BOT_TOKEN: {'***' + os.environ.get('TELEGRAM_BOT_TOKEN', '')[-4:] if os.environ.get('TELEGRAM_BOT_TOKEN') else 'YOK'}")
print(f"TELEGRAM_CHAT_ID: {os.environ.get('TELEGRAM_CHAT_ID', 'YOK')}")

# Telegram bot testini dene
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
if token:
    try:
        bot = telegram.Bot(token=token)
        me = bot.get_me()
        print(f"\nTelegram Bot Bağlantısı: BAŞARILI")
        print(f"Bot Adı: {me.first_name}")
        print(f"Bot Kullanıcı Adı: @{me.username}")
    except Exception as e:
        print(f"\nTelegram Bot Bağlantısı: BAŞARISIZ")
        print(f"Hata: {e}")
else:
    print("\nTelegram Bot Token'ı tanımlanmamış!")
