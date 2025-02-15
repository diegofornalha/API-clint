import logging
from typing import List, Dict
from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.phone_formatter import PhoneFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Z-API Configuration
INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
TOKEN = "378F94E0EAC7F1CDFFB85BC4"
DEFAULT_CLIENT_NUMBER = "21936182339"

def send_button_message():
    """Send a message with different types of buttons"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    # Define button actions
    button_actions = [
        {
            "type": "CALL",
            "phone": "5521999999999",
            "label": "📞 Call Us"
        },
        {
            "type": "URL",
            "url": "https://www.example.com",
            "label": "🌐 Visit Website"
        },
        {
            "type": "REPLY",
            "label": "✉️ Contact Support"
        }
    ]
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="Welcome to our service! Choose an option below:",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.BUTTON,
        button_actions=button_actions
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Button message sent successfully!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send button message")

def send_copy_text_button():
    """Send a message with a copy text button"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    # Create a button that copies text when clicked
    copy_code = "WELCOME2024"
    button_actions = [
        {
            "type": "URL",
            "url": f"https://www.whatsapp.com/otp/code/?otp_type=COPY_CODE&code={copy_code}",
            "label": "📋 Copy Code"
        }
    ]
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message=f"Here's your special code: {copy_code}\nClick the button below to copy it!",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.BUTTON,
        button_actions=button_actions
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Copy text button message sent successfully!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send copy text button message")

def main():
    # Test sending message with multiple button types
    logger.info("Testing message with multiple buttons...")
    send_button_message()
    
    # Test sending message with copy text button
    logger.info("\nTesting message with copy text button...")
    send_copy_text_button()

if __name__ == "__main__":
    main()