from clint_api.services.integration_service import IntegrationService
from clint_api.models.contact import Contact
from clint_api.utils.config import Config
from clint_api.utils.logger import APILogger
import time
from datetime import datetime

logger = APILogger("welcome_flow")

def wait_for_whatsapp_connection(service: IntegrationService, max_attempts: int = 5) -> bool:
    """Aguarda até que o WhatsApp esteja conectado"""
    for attempt in range(max_attempts):
        if service.zapi_client.is_connected():
            logger.info("WhatsApp conectado com sucesso!")
            return True
        
        logger.warning(f"WhatsApp não conectado. Tentativa {attempt + 1} de {max_attempts}")
        time.sleep(5)  # Espera 5 segundos antes da próxima tentativa
    
    return False

def send_welcome_message(service: IntegrationService, contact: Contact) -> None:
    """Envia mensagem de boas-vindas para um novo contato"""
    try:
        # Verifica conexão com WhatsApp
        if not wait_for_whatsapp_connection(service):
            logger.error("Não foi possível conectar ao WhatsApp após várias tentativas")
            return
        
        mensagem = (
            f"Olá {contact.name}! 👋\n\n"
            "Seja bem-vindo(a)! É um prazer ter você aqui. 🎉\n\n"
            "Estamos à disposição para ajudar no que precisar!\n\n"
            "Fique à vontade para nos enviar uma mensagem a qualquer momento. 😊"
        )
        
        result = service.send_message_to_contact(contact.id, mensagem)
        if result:
            logger.info(f"Mensagem de boas-vindas enviada com sucesso para {contact.name}")
            logger.info(f"Status da mensagem: {result.status}")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de boas-vindas: {str(e)}")

def main():
    # Valida configurações
    error = Config.validate()
    if error:
        logger.error(f"Erro de configuração: {error}")
        return
    
    # Cria o serviço de integração
    service = IntegrationService(
        clint_token=Config.CLINT_API_TOKEN,
        zapi_instance_id=Config.ZAPI_INSTANCE_ID,
        zapi_token=Config.ZAPI_TOKEN
    )
    
    try:
        # Gera um timestamp para email único
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Extrai o número do cliente das configurações
        client_number = Config.DEFAULT_CLIENT_NUMBER.replace("+", "").replace("-", "")
        ddi = "+55"  # Padrão Brasil
        phone = client_number[2:]  # Remove o DDI (55) do número
        
        # Cria o contato
        novo_contato = Contact(
            name="João da Silva",
            ddi=ddi,
            phone=phone,  # Número do cliente configurado
            email=f"joao{timestamp}@example.com",
            username=f"joaosilva{timestamp}"
        )
        
        # Cadastra o contato
        contato_criado = service.contact_client.create_contact(novo_contato)
        logger.info(f"Contato criado com sucesso! ID: {contato_criado.id}")
        
        # Envia mensagem de boas-vindas
        send_welcome_message(service, contato_criado)
        
    except Exception as e:
        logger.error(f"Erro durante o fluxo de boas-vindas: {str(e)}")

if __name__ == "__main__":
    main() 