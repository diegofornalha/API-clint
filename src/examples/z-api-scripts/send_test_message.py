from clint_api.clients.zapi_client import ZAPIClient
from clint_api.utils.logger import APILogger
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType

# Configura o logger
logger = APILogger("send_test_message")

def main():
    """Função principal"""
    # Configurações da Z-API
    INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
    TOKEN = "378F94E0EAC7F1CDFFB85BC4"
    SECURITY_TOKEN = "F0a93697fc543427aae97a54d8f03ed99S"
    
    # Número para teste
    TEST_NUMBER = "21936182339"
    
    try:
        # Cria o cliente Z-API
        client = ZAPIClient(
            instance_id=INSTANCE_ID,
            token=TOKEN,
            security_token=SECURITY_TOKEN
        )
        
        # Verifica se está conectado
        logger.info("\n🔍 Verificando status da conexão...")
        if not client.is_connected():
            logger.error("❌ WhatsApp não está conectado!")
            logger.info("Por favor:")
            logger.info("1. Acesse https://app.z-api.io")
            logger.info("2. Localize sua instância")
            logger.info("3. Faça a conexão pelo site")
            logger.info("4. Use o número 21920097294")
            return
            
        # Cria a mensagem de teste
        message = WhatsAppMessage(
            phone=TEST_NUMBER,
            message="🤖 Olá! Esta é uma mensagem de teste dos webhooks.\n\nSe você receber esta mensagem, significa que o sistema está funcionando corretamente!",
            message_type=MessageType.TEXT
        )
        
        # Envia a mensagem
        logger.info(f"\n📱 Enviando mensagem para {TEST_NUMBER}...")
        result = client.send_message(message)
        
        if result:
            logger.info("\n✅ Mensagem enviada com sucesso!")
            logger.info(f"ID da mensagem: {result.message_id}")
            logger.info("\n👀 Verifique os logs do servidor de webhooks para ver os eventos:")
            logger.info("1. Evento de mensagem enviada (on-send)")
            logger.info("2. Evento de status da mensagem (message-status)")
        else:
            logger.error("\n❌ Erro ao enviar mensagem")
            logger.info("\nVerifique:")
            logger.info("1. Se o número está conectado")
            logger.info("2. Se o número de destino é válido")
            logger.info("3. Se você tem permissão para enviar mensagens")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 