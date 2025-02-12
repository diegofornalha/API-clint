from clint_api.services.contact_service import ContactService
from clint_api.utils.logger import APILogger
from clint_api.models.contact import ContatoStatus

logger = APILogger("sync_contacts")

def main():
    service = ContactService()
    
    try:
        # Sincroniza contatos
        logger.info("\nSincronizando contatos com a API do Clint...")
        contacts = service.sync_contacts_from_clint()
        
        # Lista todos os contatos
        logger.info("\nContatos sincronizados:")
        for contact in contacts:
            logger.info(f"Nome: {contact.nome}")
            logger.info(f"Telefone: {contact.telefone}")
            logger.info(f"Status: {contact.status.value}")
            logger.info(f"Última interação: {contact.ultima_interacao}")
            logger.info("---")
        
        # Lista contatos por status
        for status in ContatoStatus:
            contacts_by_status = service.list_contacts(status)
            logger.info(f"\nContatos {status.value}: {len(contacts_by_status)}")
        
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 