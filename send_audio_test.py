import os
import base64
import requests
from clint_api.utils.logger import APILogger

# Configura o logger
logger = APILogger("send_audio_test")

def encode_audio_to_base64(audio_path: str) -> str:
    """Converte um arquivo de áudio para base64"""
    try:
        with open(audio_path, 'rb') as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            return f"data:audio/mp3;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"❌ Erro ao codificar áudio: {str(e)}")
        return None

def main():
    """Função principal"""
    # Configurações da Z-API
    INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
    TOKEN = "378F94E0EAC7F1CDFFB85BC4"
    SECURITY_TOKEN = "F0a93697fc543427aae97a54d8f03ed99S"
    
    # URL base da API
    base_url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}"
    
    # Número para teste
    TEST_NUMBER = "21936182339"
    
    # Caminho do arquivo de áudio
    AUDIO_PATH = "/Users/chain/Desktop/miniapp/API-clint/poema.mp3"
    
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
            "Client-Token": SECURITY_TOKEN,
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