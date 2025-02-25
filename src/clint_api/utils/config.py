import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
env_path = Path(__file__).parents[3] / '.env'
load_dotenv(env_path)

class Config:
    """Configurações da aplicação"""
    
    # Clint API
    CLINT_API_TOKEN: str = os.getenv('CLINT_API_TOKEN', '')
    
    # Z-API
    ZAPI_INSTANCE_ID: str = os.getenv('ZAPI_INSTANCE_ID', '')
    ZAPI_TOKEN: str = os.getenv('ZAPI_TOKEN', '')
    ZAPI_SECURITY_TOKEN: str = os.getenv('ZAPI_SECURITY_TOKEN', '')
    
    # WhatsApp Numbers
    ZAPI_SENDER_NUMBER: str = os.getenv('ZAPI_SENDER_NUMBER', '')  # Número que envia as mensagens
    DEFAULT_CLIENT_NUMBER: str = os.getenv('DEFAULT_CLIENT_NUMBER', '')  # Número padrão do cliente
    TEST_NUMBERS: dict = {
        'primary': os.getenv('TEST_NUMBER_PRIMARY', ''),
        'secondary': os.getenv('TEST_NUMBER_SECONDARY', '')
    }
    
    # Ngrok
    NGROK_AUTHTOKEN: str = os.getenv('NGROK_AUTHTOKEN', '')
    
    # Webhook
    WEBHOOK_BASE_URL: str = os.getenv('WEBHOOK_BASE_URL', '')
    WEBHOOK_PORT: int = int(os.getenv('WEBHOOK_PORT', '8000'))
    
    # Caminhos de arquivos
    AUDIO_TEST_PATH: str = os.getenv('AUDIO_TEST_PATH', '')
    
    # URLs de mídia para testes
    MEDIA_URLS = {
        'audio': os.getenv('TEST_AUDIO_URL', 'https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_100KB_MP3.mp3'),
        'video': os.getenv('TEST_VIDEO_URL', 'https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4'),
        'image': os.getenv('TEST_IMAGE_URL', 'https://www.learningcontainer.com/wp-content/uploads/2020/07/Sample-JPEG-Image-File-Download-scaled.jpg'),
        'document': os.getenv('TEST_DOCUMENT_URL', 'https://www.learningcontainer.com/wp-content/uploads/2019/09/sample-pdf-file.pdf')
    }
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """
        Valida se todas as configurações necessárias estão presentes
        
        Returns:
            Mensagem de erro se alguma configuração estiver faltando, None caso contrário
        """
        missing = []
        
        if not cls.CLINT_API_TOKEN:
            missing.append("CLINT_API_TOKEN")
        
        if not cls.ZAPI_INSTANCE_ID:
            missing.append("ZAPI_INSTANCE_ID")
        
        if not cls.ZAPI_TOKEN:
            missing.append("ZAPI_TOKEN")
        
        if not cls.ZAPI_SECURITY_TOKEN:
            missing.append("ZAPI_SECURITY_TOKEN")
        
        if not cls.ZAPI_SENDER_NUMBER:
            missing.append("ZAPI_SENDER_NUMBER")
        
        if not cls.DEFAULT_CLIENT_NUMBER:
            missing.append("DEFAULT_CLIENT_NUMBER")
        
        if not cls.NGROK_AUTHTOKEN:
            missing.append("NGROK_AUTHTOKEN")
        
        if missing:
            return f"Configurações ausentes: {', '.join(missing)}"
        
        return None
    
    @classmethod
    def get_zapi_base_url(cls) -> str:
        """Retorna a URL base do Z-API"""
        return f"https://api.z-api.io/instances/{cls.ZAPI_INSTANCE_ID}/token/{cls.ZAPI_TOKEN}"
    
    @classmethod 
    def get_test_number(cls, key: str = 'primary') -> str:
        """Retorna um número de teste"""
        return cls.TEST_NUMBERS.get(key, cls.TEST_NUMBERS.get('primary', '')) 