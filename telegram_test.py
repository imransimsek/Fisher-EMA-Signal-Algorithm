import os
import logging
import telegram
from dotenv import load_dotenv

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env dosyası yükle
load_dotenv()

# Telegram bilgileri
TOKEN = os.getenv('7288825391:AAFzbPiVIswOpzZoWsuaPE8cFETUx2N10YU')
CHAT_ID = os.getenv('926499549')

def test_telegram():
    print(f"TOKEN: {TOKEN} (Uzunluk: {len(TOKEN) if TOKEN else 0})")
    print(f"CHAT_ID: {CHAT_ID}")
    
    try:
        # Bot oluştur
        bot = telegram.Bot(token=TOKEN)
        print("Bot oluşturuldu!")
        
        # Bilgi al
        bot_info = bot.get_me()
        print(f"Bot bilgisi: {bot_info.first_name} (@{bot_info.username})")
        
        # Basit mesaj gönder
        message = "🧪 Bu bir test mesajıdır. Bot çalışıyor!"
        result = bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )
        print(f"Mesaj gönderildi! Mesaj ID: {result.message_id}")
        return True
    
    except Exception as e:
        print(f"HATA: {e}")
        return False

if __name__ == "__main__":
    print("Telegram test başlıyor...")
    result = test_telegram()
    print(f"Test sonucu: {'BAŞARILI' if result else 'BAŞARISIZ'}")
