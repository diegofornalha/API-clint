from clint_api.services.integration_service import IntegrationService
from clint_api.utils.config import Config
from clint_api.utils.logger import APILogger
import time

logger = APILogger("whatsapp_test")

def main():
    # Valida configurações
    error = Config.validate()
    if error:
        logger.error(f"Erro de configuração: {error}")
        return
    
    # Mostra configurações (sem tokens sensíveis)
    logger.info(f"Instance ID: {Config.ZAPI_INSTANCE_ID}")
    logger.info(f"Número do WhatsApp: {Config.ZAPI_SENDER_NUMBER}")
    
    # Cria o serviço de integração
    service = IntegrationService(
        clint_token=Config.CLINT_API_TOKEN,
        zapi_instance_id=Config.ZAPI_INSTANCE_ID,
        zapi_token=Config.ZAPI_TOKEN
    )
    
    try:
        # Aguarda um pouco para a conexão se estabelecer
        logger.info("Aguardando 5 segundos para a conexão se estabelecer...")
        time.sleep(5)
        
        # Testa a conexão
        logger.info(f"Testando conexão do WhatsApp para o número {Config.ZAPI_SENDER_NUMBER}...")
        
        # Tenta até 3 vezes
        for tentativa in range(3):
            logger.info(f"\nTentativa {tentativa + 1} de 3...")
            
            if service.zapi_client.is_connected():
                logger.info("✅ WhatsApp está conectado!")
                return
            else:
                logger.warning("❌ WhatsApp não está conectado!")
                if tentativa < 2:  # Se não for a última tentativa
                    logger.info("Aguardando 5 segundos antes da próxima tentativa...")
                    time.sleep(5)
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error("\nNão foi possível conectar após 3 tentativas!")
        logger.info("\nPara conectar:")
        logger.info("1. Acesse https://app.z-api.io")
        logger.info("2. Localize sua instância")
        logger.info("3. Escaneie o QR Code com o WhatsApp")
        logger.info(f"4. Use o número {Config.ZAPI_SENDER_NUMBER}")
        
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")

if __name__ == "__main__":
    main() 