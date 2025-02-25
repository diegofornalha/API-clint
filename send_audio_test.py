import os
import requests
import json
import base64
from clint_api.utils.logger import APILogger
from clint_api.utils.config import Config
from clint_api.utils.zapi_helpers import encode_media_to_base64

# Configura o logger
logger = APILogger("send_audio_test")

def encode_audio_to_base64(file_path: str) -> str:
    """Codifica um arquivo de áudio para base64"""
    return encode_media_to_base64(file_path)

def main():
    """Função principal"""
    # Verifica se a configuração é válida
    error = Config.validate()
    if error:
        logger.error(f"❌ Erro de configuração: {error}")
        return
    
    # URL base da API
    base_url = Config.get_zapi_base_url()
    
    # Número para teste
    TEST_NUMBER = Config.get_test_number('primary')
    
    # Caminho do arquivo de áudio
    AUDIO_PATH = Config.AUDIO_TEST_PATH or "/Users/chain/Desktop/miniapp/API-clint/poema.mp3"
    
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(AUDIO_PATH):
            logger.error(f"❌ Arquivo não encontrado: {AUDIO_PATH}")
            return
            
        # Converte o áudio para base64
        logger.info("\n📝 Convertendo áudio para base64...")
        base64_audio = encode_audio_to_base64(AUDIO_PATH)
        
        if not base64_audio:
            logger.error("❌ Falha ao converter áudio para base64")
            return
        
        # Headers da requisição
        headers = {
            "Client-Token": Config.ZAPI_SECURITY_TOKEN,
            "Content-Type": "application/json"
        }
        
        # Payload da requisição
        payload = {
            "phone": TEST_NUMBER,
            "audio": base64_audio,
            "waveform": True  # Opcional: mostra a forma de onda do áudio
        }
        
        # Envia o áudio
        logger.info(f"\n📱 Enviando áudio para {TEST_NUMBER}...")
        response = requests.post(
            f"{base_url}/send-audio",
            headers=headers,
            json=payload
        )
        
        # Verifica a resposta
        if response.status_code == 200:
            result = response.json()
            logger.info("\n✅ Áudio enviado com sucesso!")
            logger.info(f"zaapId: {result.get('zaapId')}")
            logger.info(f"messageId: {result.get('messageId')}")
        else:
            logger.error(f"\n❌ Erro ao enviar áudio: {response.text}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 