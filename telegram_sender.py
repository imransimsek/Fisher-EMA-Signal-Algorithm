import telegram
import logging
from typing import Dict, Any, List
import config
from datetime import datetime

# Log settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('telegram_sender')

# Create Telegram bot instance
try:
    bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)
    logger.info("Telegram bot created successfully")
except Exception as e:
    logger.error(f"Error creating Telegram bot: {e}")
    bot = None

def format_signal_message(signal: Dict[str, Any], symbol: str, interval: str) -> str:
    """
    Formats signal information into a formatted message
    """
    try:
        # Select emoji and title based on signal type
        if signal['type'] == 'EXTREME_BUY':
            emoji = "🔴"
            title = "EXTREME BUY ZONE"
            direction_emoji = "⬆️"
        elif signal['type'] == 'EXTREME_SELL':
            emoji = "🟢" 
            title = "EXTREME SELL ZONE"
            direction_emoji = "⬇️"
        elif signal['type'] == 'BUY':
            emoji = "🟢"
            title = "BUY SIGNAL"
            direction_emoji = "⬆️"
        elif signal['type'] == 'SELL':
            emoji = "🔴"
            title = "SELL SIGNAL"
            direction_emoji = "⬇️"
        else:
            emoji = "⚠️"
            title = signal['type']
            direction_emoji = "〰️"
        
        # Strength emoji
        strength_emoji = ""
        if signal.get('strength') == 'STRONG':
            strength_emoji = "💪"
        elif signal.get('strength') == 'WARNING':
            strength_emoji = "⚠️"
        elif signal.get('strength') == 'TEST':
            emoji = "🧪"
            strength_emoji = "🔍"
        
        # Date format
        time_str = "Unknown"
        if signal.get('time'):
            if hasattr(signal['time'], 'strftime'):
                time_str = signal['time'].strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(signal['time'])
        
        # Price format
        price_str = "Unknown"
        if 'price' in signal:
            price = signal['price']
            if isinstance(price, (int, float)):
                price_str = f"{price:.2f}" if price < 100 else f"{price:.1f}"
            else:
                price_str = str(price)
        
        # Message template
        message = f"{emoji} {direction_emoji} {title} {direction_emoji} {strength_emoji}\n\n"
        message += f"Symbol: {symbol}\n"
        message += f"Interval: {interval}\n"
        message += f"Price: {price_str} USDT\n"
        message += f"Zaman: {time_str}\n\n"
        
        # Indicator values
        if 'trigger' in signal:
            trigger = signal['trigger']
            trigger_str = f"{trigger:.4f}" if isinstance(trigger, (int, float)) else str(trigger)
            message += f"Trigger: {trigger_str}\n"
            
        if 'band' in signal:
            band = signal['band']
            band_str = f"{band:.4f}" if isinstance(band, (int, float)) else str(band)
            
            if signal['type'] == 'EXTREME_BUY':
                message += f"Upper Band: {band_str}\n"
            elif signal['type'] == 'EXTREME_SELL':
                message += f"Lower Band: {band_str}\n"
            else:
                message += f"Band: {band_str}\n"
                
        if 'fisher' in signal:
            fisher = signal['fisher']
            fisher_str = f"{fisher:.4f}" if isinstance(fisher, (int, float)) else str(fisher)
            message += f"Fisher: {fisher_str}\n"
        
        if 'description' in signal:
            message += f"\n📝 {signal['description']}"
        
        # Potential trade suggestion
        if signal['type'] == 'EXTREME_BUY':
            message += "\n\n⚠️ Attention: Price may be in extreme buy zone!"
        elif signal['type'] == 'EXTREME_SELL':
            message += "\n\n⚠️ Attention: Price may be in extreme sell zone!"
        
        return message
    
    except Exception as e:
        logger.error(f"Signal message formatting error: {e}")
        return f"⚠️ SIGNAL: {symbol} {interval} - Details not available"

def send_signals(signals: List[Dict[str, Any]], symbol: str, interval: str) -> bool:
    """
    Sends signals via Telegram
    
    Args:
        signals: List of signal information
        symbol: Trading pair symbol
        interval: Time interval
        
    Returns:
        True if sending is successful, False otherwise
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
            logger.info(f"Telegram message sent: {signal['type']} {symbol} {interval}")
        
        return True
    
    except Exception as e:
        logger.error(f"Telegram message sending error: {e}")
        return False

def send_simple_message(text: str) -> bool:
    """
    Sends a simple message - For test and notifications
    """
    if not bot:
        logger.error("Telegram bot not created!")
        return False
    
    try:
        bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=text
        )
        logger.info("Simple message sent")
        return True
    except Exception as e:
        logger.error(f"Simple message sending error: {e}")
        return False

def send_error_message(error_message: str, source: str = "Sistem", details: str = None) -> bool:
    """
    Sends error message to Telegram
    
    Args:
        error_message: Main error message
        source: Error source/module
        details: Error details (if applicable)
        
    Returns:
        True if sending is successful, False otherwise
    """
    if not bot:
        logger.error("Telegram bot not created - Error notification not sent!")
        return False
    
    try:
        # Mesaj şablonu
        message = f"⚠️ ERROR NOTIFICATION ⚠️\n\n"
        message += f"📋 Module: {source}\n"
        message += f"📌 Error: {error_message}\n"
        
        if details:
            message += f"\n🔍 Details: {details}\n"
            
        message += f"\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Mesajı gönder
        bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info("Error notification sent")
        return True
    
    except Exception as e:
        logger.error(f"Error notification sending error: {e}")
        return False
