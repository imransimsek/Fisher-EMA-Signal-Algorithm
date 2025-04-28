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

# Logging settings
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
    Executes processing steps for a symbol and time interval
    """
    try:
        logger.info(f"İşlem: {symbol} {interval}")
        
        # Fetch kline data
        df = fetch_klines(symbol, interval, limit=100)
        if df.empty:
            error_msg = f"Data not fetched: {symbol} {interval}"
            logger.error(error_msg)   
            return
        
        # 2. Calculate indicators
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
        
        # Log last values
        latest = df_with_indicators.iloc[-1]
        logger.info(f"Last values [{symbol}-{interval}]: Fisher={latest['fisher']:.4f}, Trigger={latest['trigger']:.4f}")
        
        # 3. Detect signals
        try:
            signals = detect_signals(df_with_indicators)
        except Exception as e:
            error_msg = f"Sinyal tespiti sırasında hata: {symbol} {interval} - {e}"
            logger.error(error_msg)
            send_error_message(error_msg, "Sinyal Tespiti", str(e))
            return
        
        # 4. Send notification to Telegram (if signals are detected)
        if signals:
            # First try direct message
            try:
                for signal in signals:
                    message = format_signal_message(signal, symbol, interval)
                    bot.send_message(
                        chat_id=config.TELEGRAM_CHAT_ID,
                        text=message,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                    logger.info(f"Signal sent directly: {signal['type']} {symbol} {interval}")
            except Exception as e:
                error_msg = f"Error sending signal: {e}"
                logger.error(error_msg)
                send_error_message(error_msg, "Telegram", f"{symbol} {interval} signal not sent")
                
                # Try alternative method
                try:
                    result = send_signals(signals, symbol, interval)
                    logger.info(f"Signal sent alternative way: {result}")
                except Exception as e2:
                    error_msg = f"Error sending signal: {e2}"
                    logger.error(error_msg)
                    send_error_message(error_msg, "Telegram", "Critical error - Signals cannot be sent!")
        else:
            logger.debug(f"No signal found: {symbol} {interval}")
    
    except Exception as e:
        error_msg = f"Error processing symbol {symbol} {interval}: {e}"
        logger.error(error_msg)
        send_error_message(error_msg, "Processing", f"General error: {str(e)}")

def run_for_interval(interval: str) -> None:
    """
    Process all symbols for a specific interval
    """
    logger.info(f"===== {interval} SCAN STARTED =====")
    for symbol in config.SYMBOLS:
        process_symbol_interval(symbol, interval)
    logger.info(f"===== {interval} SCAN COMPLETED =====")

def run_all_symbols_all_intervals() -> None:
    """
    Process all symbols and intervals for minute-based scanning
    """
    logger.info("===== MINUTE-BASED SCAN STARTED =====")
    for symbol in config.SYMBOLS:
        for interval in config.INTERVALS:
            process_symbol_interval(symbol, interval)
    logger.info("===== MINUTE-BASED SCAN COMPLETED =====")

def send_startup_notification():
    """
    Send notification to Telegram when bot starts
    """
    try:
        # Current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Monitored symbols and intervals
        symbols_str = ", ".join(config.SYMBOLS)
        intervals_str = ", ".join(config.INTERVALS)
        
        # Create message
        message = f"🤖 *Fisher + EMA Bot Started* 🤖\n\n"
        message += f"📅 Date/Time: `{current_time}`\n\n"
        message += f"👁️ Monitored Symbols: `{symbols_str}`\n"
        message += f"⏱️ Intervals: `{intervals_str}`\n\n"
        message += f"📊 Fisher Length: {config.FISHER_LENGTH}\n" 
        message += f"📈 EMA Length: {config.EMA_LENGTH}\n"
        message += f"🔍 Band Width: {config.RANGE_OFFSET}\n\n"
        message += "✅ Bot is currently running and monitoring signals!"
        
        # Doğrudan mesaj göndermeyi dene
        try:
            bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            logger.info("Startup notification sent")
            return True
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Error creating startup notification: {e}")
        return False

def send_test_signal():
    """
    Send test signal for testing purposes
    """
    try:
        # Simple test message
        message = "🧪 TEST SIGNAL 🧪\n\n"
        message += "This is a test message. If you see this message, it means the Telegram connection is working."
        
        result = send_simple_message(message)
        logger.info(f"Test message sent: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending test signal: {e}")
        return False

def schedule_jobs() -> None:
    """
    Set up schedulers
    """
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Istanbul'))
    
    # 1. Jobs based on intervals (original)
    for interval in config.INTERVALS:
        if interval == '5m':
            # Every 5 minutes: 00:00, 00:05, 00:10, ...
            for minute in range(0, 60, 5):
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')), 
                    id=f'job_{interval}_{minute}'
                )
            logger.info("5m scheduler set up")
            
        elif interval == '15m':
            # Every 15 minutes: 00:00, 00:15, 00:30, 00:45
            for minute in [0, 15, 30, 45]:
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')),
                    id=f'job_{interval}_{minute}'
                )
            logger.info("15m scheduler set up")
            
        elif interval == '30m':
            # Every 30 minutes: 00:00, 00:30
            for minute in [0, 30]:
                scheduler.add_job(
                    lambda i=interval: run_for_interval(i),
                    CronTrigger(minute=minute, timezone=pytz.timezone('Europe/Istanbul')),
                    id=f'job_{interval}_{minute}'
                )
            logger.info("30m scheduler set up")
            
        elif interval == '1h':
            # Every hour: 00:00, 01:00, 02:00, ...
            scheduler.add_job(
                lambda i=interval: run_for_interval(i),
                CronTrigger(minute=0, timezone=pytz.timezone('Europe/Istanbul')),
                id=f'job_{interval}'
            )
            logger.info("1h scheduler set up")
    
    # 2. Minute-based scanning (additional)
    scheduler.add_job(
        run_all_symbols_all_intervals,
        IntervalTrigger(minutes=1, timezone=pytz.timezone('Europe/Istanbul')),
        id='every_minute_job',
        next_run_time=datetime.now(pytz.timezone('Europe/Istanbul'))
    )
    logger.info("Minute-based scheduler set up")
    
    # Start scheduler
    scheduler.start()
    logger.info("All schedulers started")


if __name__ == "__main__":
    logger.info("Fisher + EMA Band Telegram Bot starting...")
    
    # Check environment variables (OKX instead of Binance)
    api_key = os.environ.get("OKX_API_KEY", "")
    api_secret = os.environ.get("OKX_API_SECRET", "")
    logger.info(f"OKX_API_KEY set: {'Yes' if api_key else 'No'}")
    logger.info(f"OKX_API_SECRET set: {'Yes' if api_secret else 'No'}")
    
    try:
        # Telegram test message
        logger.info("Telegram test started...")
        test_result = send_test_signal()
        
        if test_result:
            logger.info("Telegram connection is working! Bot starting...")
            
            # Send startup notification
            send_startup_notification()
            
            # Create scheduled jobs
            schedule_jobs()
            
            # Keep the main thread alive
            try:
                logger.info("Bot started. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Bot stopping...")
                # Send shutdown message
                try:
                    send_simple_message("⚠️ Bot stopped! Service is currently unavailable.")
                except Exception as e:
                    logger.error(f"Error sending shutdown message: {e}")
        else:
            error_msg = "Telegram connection failed! Bot cannot start."
            logger.error(error_msg)
            # We cannot send a message because Telegram is not working
    except Exception as e:
        error_msg = f"Unexpected error starting bot: {e}"
        logger.error(error_msg)
        # At this point, Telegram connection is not certain, so we only log
