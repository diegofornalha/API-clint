from clint_api.services.contact_service import ContactService
from clint_api.utils.logger import APILogger

logger = APILogger("check_contact_status")

def format_phone(phone: str) -> str:
    """Formata o número de telefone para o padrão do banco de dados (sem 55)"""
    # Remove caracteres não numéricos
    phone = "".join(filter(str.isdigit, phone))
    # Remove o prefixo 55 se existir
    if phone.startswith("55") and len(phone) > 2:
        phone = phone[2:]
    return phone

def main():
    service = ContactService()
    
    # Número do contato
    PHONE = "5521920097294"
    PHONE_FORMATTED = format_phone(PHONE)
    
    try:
        # Verifica status atual
        contato = service.get_contact_by_phone(PHONE_FORMATTED)
        if contato:
            logger.info(f"\nStatus do contato:")
            logger.info(f"Nome: {contato.nome}")
            logger.info(f"Telefone: {contato.telefone}")
            logger.info(f"Status: {contato.status.value}")
            logger.info(f"Última interação: {contato.ultima_interacao}")
        else:
            logger.error(f"\nContato não encontrado: {PHONE_FORMATTED}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 