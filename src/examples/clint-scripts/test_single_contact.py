from clint_api.services.contact_service import ContactService
from clint_api.models.contact import Contato, ContatoStatus
from clint_api.utils.logger import APILogger

logger = APILogger("test_single_contact")

def main():
    service = ContactService()
    
    # Dados do contato de teste
    PHONE = "21920097294"
    NAME = "Contato Teste"
    
    try:
        # Verifica se o contato já existe
        existing_contact = service.get_contact_by_phone(PHONE)
        
        if existing_contact:
            logger.info(f"\nContato já existe:")
            logger.info(f"Nome: {existing_contact.nome}")
            logger.info(f"Telefone: {existing_contact.telefone}")
            logger.info(f"Status: {existing_contact.status.value}")
            
            # Atualiza o status para inativo se necessário
            if existing_contact.status != ContatoStatus.INATIVO:
                existing_contact = service.update_contact_status(PHONE, ContatoStatus.INATIVO)
                logger.info(f"\nStatus atualizado para: {existing_contact.status.value}")
        else:
            # Cria novo contato
            novo_contato = Contato(
                nome=NAME,
                telefone=PHONE,
                status=ContatoStatus.INATIVO
            )
            service.session.add(novo_contato)
            service.session.commit()
            logger.info(f"\nNovo contato adicionado:")
            logger.info(f"Nome: {novo_contato.nome}")
            logger.info(f"Telefone: {novo_contato.telefone}")
            logger.info(f"Status: {novo_contato.status.value}")
        
        # Lista todos os contatos inativos para confirmar
        inativos = service.get_inactive_contacts()
        logger.info(f"\nTotal de contatos inativos: {len(inativos)}")
        logger.info("\nContatos inativos:")
        for contato in inativos:
            if contato.telefone == PHONE:
                logger.info("=== CONTATO DE TESTE ===")
            logger.info(f"Nome: {contato.nome}")
            logger.info(f"Telefone: {contato.telefone}")
            logger.info(f"Status: {contato.status.value}")
            logger.info("---")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 