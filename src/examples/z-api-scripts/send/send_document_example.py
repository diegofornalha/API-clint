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

def send_document_by_url():
    """Send a document using URL method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    # Example document URL (replace with a valid document URL)
    document_url = "https://example.com/test-document.pdf"
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.DOCUMENT,
        media_url=document_url,
        caption="This is a test document sent via URL 📄"
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Document sent successfully via URL!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send document via URL")

def encode_document_to_base64(document_path: str) -> Optional[str]:
    """Convert a document file to base64 string"""
    try:
        with open(document_path, 'rb') as document_file:
            encoded_string = base64.b64encode(document_file.read()).decode('utf-8')
            # Get file extension
            file_extension = os.path.splitext(document_path)[1].lower()
            mime_type = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain'
            }.get(file_extension, 'application/octet-stream')
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Error encoding document: {str(e)}")
        return None

def send_document_by_base64(document_path: str):
    """Send a document using Base64 method"""
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    base64_document = encode_document_to_base64(document_path)
    if not base64_document:
        logger.error("❌ Failed to encode document to base64")
        return
    
    message = WhatsAppMessage(
        phone=DEFAULT_CLIENT_NUMBER,
        message="",
        instance_id=INSTANCE_ID,
        token=TOKEN,
        message_type=MessageType.DOCUMENT,
        media_url=base64_document,
        caption="This is a test document sent via Base64 📄"
    )
    
    result = client.send_message(message)
    if result and result.message_id:
        logger.info("✅ Document sent successfully via Base64!")
        logger.info(f"Message ID: {result.message_id}")
    else:
        logger.error("❌ Failed to send document via Base64")

def main():
    # Test sending document by URL
    logger.info("Testing document sending via URL...")
    send_document_by_url()
    
    # Test sending document by Base64
    # Replace with path to a test document
    test_document_path = "path/to/your/test/document.pdf"
    if os.path.exists(test_document_path):
        logger.info("\nTesting document sending via Base64...")
        send_document_by_base64(test_document_path)
    else:
        logger.error(f"\n❌ Test document not found at: {test_document_path}")

if __name__ == "__main__":
    main()