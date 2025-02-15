import os
import base64
import logging
from typing import Optional
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

def send_audio_by_url():
    """Send an audio using URL method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    # Example audio URL (replace with a valid audio URL)
    audio_url = "https://example.com/test-audio.mp3"
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.AUDIO,
        media_url=audio_url
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Audio sent successfully via URL!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send audio via URL")

def encode_audio_to_base64(audio_path: str) -> Optional[str]:
    """Convert an audio file to base64 string"""
    try:
        with open(audio_path, 'rb') as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            return f"data:audio/mp3;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Error encoding audio: {str(e)}")
        return None

def send_audio_by_base64(audio_path: str):
    """Send an audio using Base64 method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    base64_audio = encode_audio_to_base64(audio_path)
    if not base64_audio:
        logger.error("❌ Failed to encode audio to base64")
        return
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.AUDIO,
        media_url=base64_audio
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Audio sent successfully via Base64!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send audio via Base64")

def main():
    # Test sending audio by URL
    logger.info("Testing audio sending via URL...")
    send_audio_by_url()
    
    # Test sending audio by Base64
    # Replace with path to a test audio file
    test_audio_path = "path/to/your/test/audio.mp3"
    if os.path.exists(test_audio_path):
        logger.info("\nTesting audio sending via Base64...")
        send_audio_by_base64(test_audio_path)
    else:
        logger.error(f"\n❌ Test audio not found at: {test_audio_path}")

if __name__ == "__main__":
    main()