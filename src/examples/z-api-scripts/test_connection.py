from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.logger import APILogger
import time

logger = APILogger("test_connection")

def wait_for_connection(client: ZAPIClient, max_attempts: int = 3) -> bool:
    """Aguarda até que o WhatsApp esteja conectado"""
    for attempt in range(max_attempts):
        logger.info(f"\nTentativa {attempt + 1} de {max_attempts} de conexão...")
        
        if client.is_connected():
            logger.info("✅ WhatsApp conectado!")
            return True
        
        if attempt < max_attempts - 1:
            logger.info("Aguardando 5 segundos antes da próxima tentativa...")
            time.sleep(5)
    
    return False

def main():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    
    # Número do destinatário
    PHONE = "5521920097294"
    
    # Criando cliente Z-API
    client = ZAPIClient(INSTANCE_ID, TOKEN)
    
    try:
        # Verifica se está conectado
        if not wait_for_connection(client):
            logger.error("\n❌ WhatsApp não está conectado!")
            logger.info("\nPara conectar:")
            logger.info("1. Acesse https://app.z-api.io")
            logger.info("2. Localize sua instância")
            logger.info("3. Escaneie o QR Code com o WhatsApp")
            logger.info("4. Use o número 21936182339")
            return
            
        # Cria a mensagem
        message = WhatsAppMessage(
            phone=PHONE,
            message="Olá! Esta é uma mensagem de teste para verificar a conexão com a Z-API. 👋\nHora do envio: " + time.strftime("%H:%M:%S"),
            instance_id=INSTANCE_ID,
            token=TOKEN,
            message_type=MessageType.TEXT
        )
        
        # Envia a mensagem
        logger.info(f"\nEnviando mensagem para {PHONE}...")
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