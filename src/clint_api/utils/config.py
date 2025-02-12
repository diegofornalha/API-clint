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
    
    # Ngrok
    NGROK_AUTHTOKEN: str = os.getenv('NGROK_AUTHTOKEN', '')
    
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