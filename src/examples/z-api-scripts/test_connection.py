import time
from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.logger import APILogger
from clint_api.utils.config import Config
from clint_api.utils.zapi_helpers import check_connection

logger = APILogger("test_connection")

def wait_for_connection(client: ZAPIClient, max_attempts: int = 5, wait_time: int = 5) -> bool:
    """Espera até que o WhatsApp esteja conectado"""
    logger.info("\nVerificando conexão com WhatsApp...")
    
    for i in range(max_attempts):
        if i > 0:
            logger.info(f"\nTentativa {i+1} de {max_attempts}...")
            
        if client.is_connected():
            logger.info("\n✅ WhatsApp conectado!")
            return True
            
        logger.info(f"\nAguardando {wait_time} segundos...")
        time.sleep(wait_time)
    
    return False

def main():
    # Verifica se a configuração é válida
    error = Config.validate()
    if error:
        logger.error(f"❌ Erro de configuração: {error}")
        return
    
    # Criando cliente Z-API com dados da configuração
    client = ZAPIClient(
        instance_id=Config.ZAPI_INSTANCE_ID,
        token=Config.ZAPI_TOKEN,
        security_token=Config.ZAPI_SECURITY_TOKEN
    )
    
    try:
        # Verifica se está conectado usando a função auxiliar
        if not check_connection(client):
            return
            
        # Obtém o número de teste da configuração
        test_phone = Config.get_test_number()
        
        # Cria a mensagem
        message = WhatsAppMessage(
            phone=test_phone,
            message="Olá! Esta é uma mensagem de teste para verificar a conexão com a Z-API. 👋\nHora do envio: " + time.strftime("%H:%M:%S"),
            message_type=MessageType.TEXT
        )
        
        # Envia a mensagem
        logger.info(f"\nEnviando mensagem para {test_phone}...")
        result = client.send_message(message)
        
        if result and result.message_id:
            logger.info(f"\n✅ Mensagem enviada com sucesso!")
            logger.info(f"ID da mensagem: {result.message_id}")
            logger.info(f"Status: {result.status}")
        else:
            logger.error("\n❌ Erro ao enviar mensagem")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 