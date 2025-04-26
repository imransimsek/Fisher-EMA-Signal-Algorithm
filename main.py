import logging
import time
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import telegram
import os

import config
from okx_client import fetch_klines
from indicators import fisher_ema_band
from signal_detector import detect_signals
from telegram_sender import send_signals, bot, format_signal_message, send_error_message, send_simple_message

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fisher_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

def process_symbol_interval(symbol: str, interval: str) -> None:
    """
    Bir sembol ve zaman dilimi için işlem adımlarını çalıştırır
    """
    try:
        logger.info(f"İşlem: {symbol} {interval}")
        
        # 1. Verileri çek
        df = fetch_klines(symbol, interval, limit=100)
        if df.empty:
            error_msg = f"Veri çekilemedi: {symbol} {interval}"
            logger.error(error_msg)
            # (fetch_klines içinde zaten bildirim gönderiliyor)
            return
        
        # 2. İndikatörü hesapla
        try:
            df_with_indicators = fisher_ema_band(
                df, 
                length=config.FISHER_LENGTH,
                ema_length=config.EMA_LENGTH,
                range_offset=config.RANGE_OFFSET
            )
        except Exception as e:
            error_msg = f"İndikatör hesaplanırken hata: {symbol} {interval} - {e}"
            logger.error(error_msg)
            send_error_message(error_msg, "İndikatör", str(e))
            return
        
        # Log son değerleri
        latest = df_with_indicators.iloc[-1]
        logger.info(f"Son değerler [{symbol}-{interval}]: Fisher={latest['fisher']:.4f}, Trigger={latest['trigger']:.4f}")
        
        # 3. Sinyalleri tespit et
        try:
            signals = detect_signals(df_with_indicators)
        except Exception as e:
            error_msg = f"Sinyal tespiti sırasında hata: {symbol} {interval} - {e}"
            logger.error(error_msg)
            send_error_message(error_msg, "Sinyal Tespiti", str(e))
            return
        
        # 4. Telegram'a bildir (sinyal varsa)
        if signals:
            # Önce doğrudan mesaj göndermeyi dene
            try:
                for signal in signals:
                    message = format_signal_message(signal, symbol, interval)
                    bot.send_message(
                        chat_id=config.TELEGRAM_CHAT_ID,
                        text=message,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                    logger.info(f"Sinyal doğrudan gönderildi: {signal['type']} {symbol} {interval}")
            except Exception as e:
                error_msg = f"Sinyal gönderiminde hata: {e}"
                logger.error(error_msg)
                send_error_message(error_msg, "Telegram", f"{symbol} {interval} için sinyal gönderilemedi")
                
                # Alternatif yöntem ile dene
                try:
                    result = send_signals(signals, symbol, interval)
                    logger.info(f"Sinyal alternatif yolla gönderildi: {result}")
                except Exception as e2:
                    error_msg = f"Alternatif sinyal gönderiminde de hata: {e2}"
                    logger.error(error_msg)
                    send_error_message(error_msg, "Telegram", "Kritik hata - Sinyaller iletilemiyor!")
        else:
            logger.debug(f"Sinyal bulunamadı: {symbol} {interval}")
    
    except Exception as e:
        error_msg = f"İşlem hatası: {symbol} {interval} - {e}"
        logger.error(error_msg)
        send_error_message(error_msg, "İşlem", f"Genel hata: {str(e)}")

def run_for_interval(interval: str) -> None:
    """
    Belirli bir zaman dilimi için tüm sembolleri işler
    """
    logger.info(f"===== {interval} TARAMASI BAŞLADI =====")
    for symbol in config.SYMBOLS:
        process_symbol_interval(symbol, interval)
    logger.info(f"===== {interval} TARAMASI TAMAMLANDI =====")

def run_all_symbols_all_intervals() -> None:
    """
    Tüm sembol ve zaman dilimlerini dakikalık tarama için işler
    """
    logger.info("===== DAKİKALIK TARAMA BAŞLADI =====")
    for symbol in config.SYMBOLS:
        for interval in config.INTERVALS:
            process_symbol_interval(symbol, interval)
    logger.info("===== DAKİKALIK TARAMA TAMAMLANDI =====")

def send_startup_notification():
    """
    Bot başlatıldığında Telegram'a bildirim gönderir
    """
    try:
        # Mevcut zaman
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # İzlenen sembol ve zaman dilimleri
        symbols_str = ", ".join(config.SYMBOLS)
        intervals_str = ", ".join(config.INTERVALS)
        
        # Mesaj oluştur
        message = f"🤖 *Fisher + EMA Bot Başlatıldı* 🤖\n\n"
        message += f"📅 Tarih/Saat: `{current_time}`\n\n"
        message += f"👁️ İzlenen Semboller: `{symbols_str}`\n"
        message += f"⏱️ Zaman Dilimleri: `{intervals_str}`\n\n"
        message += f"📊 Fisher Uzunluk: {config.FISHER_LENGTH}\n" 
        message += f"📈 EMA Uzunluk: {config.EMA_LENGTH}\n"
        message += f"🔍 Bant Genişliği: {config.RANGE_OFFSET}\n\n"
        message += "✅ Bot şu anda çalışıyor ve sinyalleri izliyor!"
        
        # Doğrudan mesaj göndermeyi dene
        try:
            bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            logger.info("Başlangıç bildirimi gönderildi")
            return True
        except Exception as e:
            logger.error(f"Başlangıç bildirimi gönderiminde hata: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Başlangıç bildirimi oluşturmada hata: {e}")
        return False

def send_test_signal():
    """
    Test amaçlı sinyal gönderir
    """
    try:
        # Basit test mesajı
        message = "🧪 TEST SİNYALİ 🧪\n\n"
        message += "Bu bir test mesajıdır. Eğer bu mesajı görüyorsanız, Telegram bağlantısı çalışıyor demektir."
        
        result = send_simple_message(message)
        logger.info(f"Test mesajı gönderildi: {result}")
        return result
    except Exception as e:
        logger.error(f"Test sinyali gönderiminde hata: {e}")
        return False

def schedule_jobs() -> None:
    """
    Zamanlayıcıları ayarlar
    """
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Istanbul'))
    
    # 1. Zaman dilimlerine bağlı işler (orijinal)
    for interval in config.INTERVALS:
        if interval == '5m':
            # Her 5 dakikada bir: 00:00, 00:05, 00:10, ...
            for minute in range(0, 60, 5):
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')), 
                    id=f'job_{interval}_{minute}'
                )
            logger.info("5m zamanlayıcı ayarlandı")
            
        elif interval == '15m':
            # Her 15 dakikada bir: 00:00, 00:15, 00:30, 00:45
            for minute in [0, 15, 30, 45]:
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')),
                    id=f'job_{interval}_{minute}'
                )
            logger.info("15m zamanlayıcı ayarlandı")
            
        elif interval == '30m':
            # Her 30 dakikada bir: 00:00, 00:30
            for minute in [0, 30]:
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')),
                    id=f'job_{interval}_{minute}'
                )
            logger.info("30m zamanlayıcı ayarlandı")
            
        elif interval == '1h':
            # Her saatte bir: 00:00, 01:00, 02:00, ...
            scheduler.add_job(
                lambda i=interval: run_for_interval(i),
                CronTrigger(minute=0, timezone=pytz.timezone('Europe/Istanbul')),
                id=f'job_{interval}'
            )
            logger.info("1h zamanlayıcı ayarlandı")
    
    # 2. Dakikalık tarama (ek olarak)
    scheduler.add_job(
        run_all_symbols_all_intervals,
        IntervalTrigger(minutes=1, timezone=pytz.timezone('Europe/Istanbul')),
        id='every_minute_job',
        next_run_time=datetime.now(pytz.timezone('Europe/Istanbul'))
    )
    logger.info("Dakikalık zamanlayıcı ayarlandı")
    
    # Zamanlayıcıyı başlat
    scheduler.start()
    logger.info("Tüm zamanlayıcılar başlatıldı")


if __name__ == "__main__":
    logger.info("Fisher + EMA Band Telegram Bot başlatılıyor...")
    
    # Ortam değişkenlerini kontrol et (Binance yerine OKX)
    api_key = os.environ.get("OKX_API_KEY", "")
    api_secret = os.environ.get("OKX_API_SECRET", "")
    logger.info(f"OKX_API_KEY ayarlandı mı: {'Evet' if api_key else 'Hayır'}")
    logger.info(f"OKX_API_SECRET ayarlandı mı: {'Evet' if api_secret else 'Hayır'}")
    
    try:
        # Telegram test mesajı gönder
        logger.info("Telegram testi yapılıyor...")
        test_result = send_test_signal()
        
        if test_result:
            logger.info("Telegram bağlantısı çalışıyor! Bot başlatılıyor...")
            
            # Bot başlangıç bildirimini gönder
            send_startup_notification()
            
            # Zamanlanmış işleri oluştur
            schedule_jobs()
            
            # Programın sonlanmaması için ana thread'i canlı tut
            try:
                logger.info("Bot çalışmaya başladı. Çıkmak için Ctrl+C'ye basın.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Bot kapatılıyor...")
                # Bot kapanış mesajı gönder
                try:
                    send_simple_message("⚠️ Bot kapatıldı! Hizmet şu anda devre dışı.")
                except Exception as e:
                    logger.error(f"Kapanış mesajı gönderilirken hata: {e}")
        else:
            error_msg = "Telegram bağlantısı kurulamadı! Bot başlatılamıyor."
            logger.error(error_msg)
            # Bu durumda mesaj gönderemeyiz çünkü Telegram zaten çalışmıyor
    except Exception as e:
        error_msg = f"Bot başlatılırken beklenmeyen hata: {e}"
        logger.error(error_msg)
        # Şu aşamada telegram bağlantısı belli değil, bu yüzden sadece logluyoruz
