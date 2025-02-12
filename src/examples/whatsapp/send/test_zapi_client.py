from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.logger import APILogger
from clint_api.utils.phone_formatter import PhoneFormatter
import time

logger = APILogger("test_zapi_client")

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
    SECURITY_TOKEN = "Fd07396a2aa4547d1a45a70acce79a22dS"
    
    # Número do destinatário
    PHONE = "21920097294"  # Número sem prefixo
    
    # Valida o número
    if not PhoneFormatter.is_valid(PHONE):
        logger.error(f"\n❌ Número de telefone inválido: {PHONE}")
        return
        
    # Extrai informações do número
    phone_info = PhoneFormatter.extract_info(PHONE)
    if not phone_info:
        logger.error(f"\n❌ Não foi possível extrair informações do número: {PHONE}")
        return
        
    logger.info("\nInformações do número:")
    logger.info(f"DDI: +{phone_info['ddi']}")
    logger.info(f"DDD: {phone_info['ddd']}")
    logger.info(f"Número: {phone_info['number']}")
    logger.info(f"Formato para API: {phone_info['formatted']['api']}")
    logger.info(f"Formato para exibição: {phone_info['formatted']['display']}")
    
    # Criando cliente Z-API
    client = ZAPIClient(
        instance_id=INSTANCE_ID,
        token=TOKEN,
        security_token=SECURITY_TOKEN
    )
    
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
            phone=phone_info['formatted']['api'],  # Usa o formato para API
            message="Olá! Esta é uma mensagem de teste do sistema usando o ZAPIClient atualizado. 👋\n\n"
                   f"Hora do envio: {time.strftime('%H:%M:%S')}",
            instance_id=INSTANCE_ID,
            token=TOKEN,
            message_type=MessageType.TEXT
        )
        
        # Envia a mensagem
        logger.info(f"\nEnviando mensagem para {phone_info['formatted']['display']}...")
        result = client.send_message(message)
        
        if result and result.message_id:
            logger.info(f"\n✅ Mensagem enviada com sucesso!")
            logger.info(f"Message ID: {result.message_id}")
            logger.info(f"Status: {result.status}")
        else:
            logger.error("\n❌ Erro ao enviar mensagem")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 