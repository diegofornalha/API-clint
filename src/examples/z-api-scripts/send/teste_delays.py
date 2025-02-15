from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.logger import APILogger
import time

logger = APILogger("teste_delays")

def testar_delays():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    SECURITY_TOKEN = "Fd07396a2aa4547d1a45a70acce79a22dS"
    
    # Número de teste (substitua pelo seu número)
    TELEFONE = "5521920097294"
    
    # Criando cliente Z-API
    cliente = ZAPIClient(INSTANCE_ID, TOKEN, SECURITY_TOKEN)
    
    # Mensagens de teste com diferentes tamanhos
    mensagens = [
        "Olá! 👋",  # Mensagem curta
        "Esta é uma mensagem de tamanho médio para testar os delays. 📝",  # Média
        "Esta é uma mensagem mais longa para testarmos como o sistema ajusta os tempos de delay e digitação de forma automática baseado no tamanho do texto. Quanto maior a mensagem, maior será o tempo simulando a digitação para parecer mais natural. 🤖✨"  # Longa
    ]
    
    try:
        # Verifica conexão
        if not cliente.is_connected():
            logger.error("❌ WhatsApp não está conectado!")
            return
            
        logger.info("✅ WhatsApp conectado! Iniciando testes...\n")
        
        # Testa cada mensagem
        for i, texto in enumerate(mensagens, 1):
            logger.info(f"\nTeste #{i} - Mensagem com {len(texto)} caracteres")
            logger.info("Texto: " + texto)
            
            # Calcula os delays que serão usados
            delay_message = max(2, len(texto) // 20)
            delay_typing = max(3, len(texto) // 15)
            
            logger.info(f"Delay de mensagem: {delay_message} segundos")
            logger.info(f"Tempo digitando: {delay_typing} segundos")
            
            # Cria e envia a mensagem
            mensagem = WhatsAppMessage(
                phone=TELEFONE,
                message=texto,
                message_type=MessageType.TEXT
            )
            
            resultado = cliente.send_message(mensagem)
            
            if resultado and resultado.message_id:
                logger.info(f"✅ Mensagem enviada com sucesso!")
                logger.info(f"ID: {resultado.message_id}")
            else:
                logger.error("❌ Erro ao enviar mensagem")
                
            # Aguarda entre os testes
            if i < len(mensagens):
                logger.info("\nAguardando 5 segundos antes do próximo teste...")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    testar_delays()