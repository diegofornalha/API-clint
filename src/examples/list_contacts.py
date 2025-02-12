import os
import sys

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clint_api.services.contact_service import ContactService
from clint_api.utils.logger import APILogger

logger = APILogger("list_contacts")

def main():
    service = ContactService()
    
    try:
        # Lista todos os contatos
        contacts = service.list_contacts()
        
        for contact in contacts:
            logger.info(f"Nome: {contact.nome}")
            logger.info(f"Telefone: {contact.telefone}")
            logger.info(f"Status: {contact.status.value}")
            logger.info(f"Tags: {contact.tags}")
            logger.info(f"Última interação: {contact.ultima_interacao}")
            logger.info("---")
            
        # Contagem por status
        status_count = {}
        for contact in contacts:
            if contact.status.value not in status_count:
                status_count[contact.status.value] = 0
            status_count[contact.status.value] += 1
            
        logger.info("\nContagem por status:")
        for status, count in status_count.items():
            logger.info(f"{status}: {count}")
            
    except Exception as e:
        logger.error(f"Erro: {str(e)}")

if __name__ == "__main__":
    main() 