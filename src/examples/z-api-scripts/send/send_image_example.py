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

def send_image_by_url():
    """Send an image using URL method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    # Example image URL (replace with a valid image URL)
    image_url = "https://example.com/test-image.jpg"
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",  # Optional caption
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.IMAGE,
        media_url=image_url,
        caption="This is a test image sent via URL 📸"
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Image sent successfully via URL!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send image via URL")

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Convert an image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}")
        return None

def send_image_by_base64(image_path: str):
    """Send an image using Base64 method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        logger.error("❌ Failed to encode image to base64")
        return
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.IMAGE,
        media_url=base64_image,
        caption="This is a test image sent via Base64 📸"
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Image sent successfully via Base64!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send image via Base64")

def main():
    # Test sending image by URL
    logger.info("Testing image sending via URL...")
    send_image_by_url()
    
    # Test sending image by Base64
    # Replace with path to a test image
    test_image_path = "path/to/your/test/image.jpg"
    if os.path.exists(test_image_path):
        logger.info("\nTesting image sending via Base64...")
        send_image_by_base64(test_image_path)
    else:
        logger.error(f"\n❌ Test image not found at: {test_image_path}")

if __name__ == "__main__":
    main()