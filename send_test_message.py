from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.logger import APILogger
import time

logger = APILogger('test_message')

# Configurações do Z-API do arquivo .env
INSTANCE_ID = '3DCC625CC314A038C87896155CBF9532'
TOKEN = '378F94E0EAC7F1CDFFB85BC4'
SECURITY_TOKEN = 'F0a93697fc543427aae97a54d8f03ed99S'
DEFAULT_CLIENT_NUMBER = '21998567176'

def main():
    # Criando cliente Z-API
    client = ZAPIClient(INSTANCE_ID, TOKEN, SECURITY_TOKEN)

    try:
        # Verifica conexão
        if not client.is_connected():
            logger.error('❌ WhatsApp não está conectado!')
            logger.info('\nPara conectar:')
            logger.info('1. Acesse https://app.z-api.io')
            logger.info('2. Localize sua instância')
            logger.info('3. Escaneie o QR Code com o WhatsApp')
            return

        # Cria a mensagem
        message = WhatsAppMessage(
            phone=DEFAULT_CLIENT_NUMBER,
            message='Olá! Esta é uma mensagem de teste do sistema. 👋\n\nHora do envio: ' + time.strftime('%H:%M:%S'),
            instance_id=INSTANCE_ID,
            token=TOKEN,
            message_type=MessageType.TEXT
        )

        # Envia a mensagem
        logger.info(f'Enviando mensagem para {DEFAULT_CLIENT_NUMBER}...')
        result = client.send_message(message)

        if result and result.message_id:
            logger.info('✅ Mensagem enviada com sucesso!')
            logger.info(f'Message ID: {result.message_id}')
            logger.info(f'Status: {result.status}')
        else:
            logger.error('❌ Erro ao enviar mensagem')

    except Exception as e:
        logger.error(f'❌ Erro: {str(e)}')

if __name__ == '__main__':
    main() 