from clint_api.services.contact_service import ContactService
from clint_api.utils.phone_formatter import PhoneFormatter
from clint_api.utils.logger import APILogger
from dotenv import load_dotenv
import os

logger = APILogger("test_phone_numbers")

def test_phone_number(phone: str, description: str):
    """Test a phone number for validity and formatting"""
    service = ContactService()
    
    logger.info(f"\nTesting {description}: {phone}")
    
    # Test validity
    is_valid = service.is_valid_phone(phone)
    logger.info(f"Is valid: {is_valid}")
    
    if is_valid:
        # Test database formatting
        db_format = PhoneFormatter.format_to_db(phone)
        logger.info(f"DB format: {db_format}")
        
        # Test API formatting
        api_format = PhoneFormatter.format_to_api(phone)
        logger.info(f"API format: {api_format}")
        
        # Get detailed info
        info = PhoneFormatter.extract_info(phone)
        if info:
            logger.info(f"Detailed info:")
            logger.info(f"DDI: {info['ddi']}")
            logger.info(f"DDD: {info['ddd']}")
            logger.info(f"Number: {info['number']}")
            logger.info(f"Display format: {info['formatted']['display']}")
    
    logger.info("---")

def main():
    load_dotenv()
    
    # Get phone numbers from .env
    sender_number = os.getenv("ZAPI_SENDER_NUMBER")
    client_number = os.getenv("DEFAULT_CLIENT_NUMBER")
    
    # Test each number
    if sender_number:
        test_phone_number(sender_number, "Sender number")
    
    if client_number:
        test_phone_number(client_number, "Client number")

if __name__ == "__main__":
    main()