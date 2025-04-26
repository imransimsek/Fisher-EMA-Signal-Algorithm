import telegram
import logging
from typing import Dict, Any, List
import config
from datetime import datetime

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('telegram_sender')

# Telegram Bot örneği oluştur
try:
    bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)
    logger.info("Telegram botu başarıyla oluşturuldu")
except Exception as e:
    logger.error(f"Telegram botu oluşturulurken hata: {e}")
    bot = None

def format_signal_message(signal: Dict[str, Any], symbol: str, interval: str) -> str:
    """
    Sinyal bilgilerini biçimlendirilmiş mesaja dönüştürür
    """
    try:
        # Sinyal tipine göre emoji ve başlık seç
        if signal['type'] == 'AŞIRI_ALIM':
            emoji = "🔴"
            title = "AŞIRI ALIM BÖLGESİ"
            direction_emoji = "⬆️"
        elif signal['type'] == 'AŞIRI_SATIM':
            emoji = "🟢" 
            title = "AŞIRI SATIM BÖLGESİ"
            direction_emoji = "⬇️"
        elif signal['type'] == 'AL':
            emoji = "🟢"
            title = "AL SİNYALİ"
            direction_emoji = "⬆️"
        elif signal['type'] == 'SAT':
            emoji = "🔴"
            title = "SAT SİNYALİ"
            direction_emoji = "⬇️"
        else:
            emoji = "⚠️"
            title = signal['type']
            direction_emoji = "〰️"
        
        # Güç emojisi
        strength_emoji = ""
        if signal.get('strength') == 'GÜÇLÜ':
            strength_emoji = "💪"
        elif signal.get('strength') == 'UYARI':
            strength_emoji = "⚠️"
        elif signal.get('strength') == 'TEST':
            emoji = "🧪"
            strength_emoji = "🔍"
        
        # Tarih formatı
        time_str = "Bilinmiyor"
        if signal.get('time'):
            if hasattr(signal['time'], 'strftime'):
                time_str = signal['time'].strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(signal['time'])
        
        # Fiyat formatı
        price_str = "Bilinmiyor"
        if 'price' in signal:
            price = signal['price']
            if isinstance(price, (int, float)):
                price_str = f"{price:.2f}" if price < 100 else f"{price:.1f}"
            else:
                price_str = str(price)
        
        # Mesaj şablonu
        message = f"{emoji} {direction_emoji} {title} {direction_emoji} {strength_emoji}\n\n"
        message += f"Sembol: {symbol}\n"
        message += f"Zaman Dilimi: {interval}\n"
        message += f"Fiyat: {price_str} USDT\n"
        message += f"Zaman: {time_str}\n\n"
        
        # İndikatör değerleri
        if 'trigger' in signal:
            trigger = signal['trigger']
            trigger_str = f"{trigger:.4f}" if isinstance(trigger, (int, float)) else str(trigger)
            message += f"Trigger: {trigger_str}\n"
            
        if 'band' in signal:
            band = signal['band']
            band_str = f"{band:.4f}" if isinstance(band, (int, float)) else str(band)
            
            if signal['type'] == 'AŞIRI_ALIM':
                message += f"Üst Band: {band_str}\n"
            elif signal['type'] == 'AŞIRI_SATIM':
                message += f"Alt Band: {band_str}\n"
            else:
                message += f"Band: {band_str}\n"
                
        if 'fisher' in signal:
            fisher = signal['fisher']
            fisher_str = f"{fisher:.4f}" if isinstance(fisher, (int, float)) else str(fisher)
            message += f"Fisher: {fisher_str}\n"
        
        if 'description' in signal:
            message += f"\n📝 {signal['description']}"
        
        # Potansiyel işlem önerisi
        if signal['type'] == 'AŞIRI_ALIM':
            message += "\n\n⚠️ Dikkat: Fiyat aşırı alım bölgesinde olabilir!"
        elif signal['type'] == 'AŞIRI_SATIM':
            message += "\n\n⚠️ Dikkat: Fiyat aşırı satım bölgesinde olabilir!"
        
        return message
    
    except Exception as e:
        logger.error(f"Sinyal mesajı biçimlendirme hatası: {e}")
        return f"⚠️ SINYAL: {symbol} {interval} - Detaylar gösterilemiyor"

def send_signals(signals: List[Dict[str, Any]], symbol: str, interval: str) -> bool:
    """
    Sinyalleri Telegram üzerinden gönderir
    
    Args:
        signals: Sinyal bilgilerini içeren liste
        symbol: İşlem çifti sembolü
        interval: Zaman dilimi
        
    Returns:
        Gönderim başarılıysa True, değilse False
    """
    if not bot or not signals:
        return False
    
    try:
        for signal in signals:
            message = format_signal_message(signal, symbol, interval)
            bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            logger.info(f"Telegram mesajı gönderildi: {signal['type']} {symbol} {interval}")
        
        return True
    
    except Exception as e:
        logger.error(f"Telegram mesajı gönderilirken hata: {e}")
        return False

def send_simple_message(text: str) -> bool:
    """
    Basit bir mesaj gönderir - Test ve bildirimler için
    """
    if not bot:
        logger.error("Telegram botu oluşturulmamış!")
        return False
    
    try:
        bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=text
        )
        logger.info("Basit mesaj gönderildi")
        return True
    except Exception as e:
        logger.error(f"Basit mesaj gönderilirken hata: {e}")
        return False

def send_error_message(error_message: str, source: str = "Sistem", details: str = None) -> bool:
    """
    Hata mesajını Telegram'a bildirir
    
    Args:
        error_message: Ana hata mesajı
        source: Hatanın kaynağı/modülü
        details: Hata detayları (varsa)
        
    Returns:
        Gönderim başarılıysa True, değilse False
    """
    if not bot:
        logger.error("Telegram botu oluşturulmamış - Hata bildirimi yapılamadı!")
        return False
    
    try:
        # Mesaj şablonu
        message = f"⚠️ HATA BİLDİRİMİ ⚠️\n\n"
        message += f"📋 Modül: {source}\n"
        message += f"📌 Hata: {error_message}\n"
        
        if details:
            message += f"\n🔍 Detaylar: {details}\n"
            
        message += f"\n⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Mesajı gönder
        bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info("Hata bildirimi gönderildi")
        return True
    
    except Exception as e:
        logger.error(f"Hata bildirimi gönderilirken başka bir hata oluştu: {e}")
        return False
