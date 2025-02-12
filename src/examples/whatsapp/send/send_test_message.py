import requests
import json
from datetime import datetime
from clint_api.utils.logger import APILogger

logger = APILogger("send_test_message")

def send_message():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    SECURITY_TOKEN = "Fd07396a2aa4547d1a45a70acce79a22dS"
    
    # Formata o número (remove caracteres especiais)
    PHONE = "5521920097294"  # Formatado: 55 + DDD + número
    
    # URL da API (usando a versão que funcionou)
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-text"
    
    # Headers (incluindo o SECURITY_TOKEN)
    headers = {
        "Client-Token": SECURITY_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Mensagem personalizada
    message = (
        "Olá! Esta é uma mensagem de teste do sistema. 👋\n\n"
        f"Hora do envio: {datetime.now().strftime('%H:%M:%S')}"
    )
    
    # Payload (incluindo delays)
    payload = {
        "phone": PHONE,
        "message": message,
        "delayMessage": 2,  # 2 segundos de delay
        "delayTyping": 3    # 3 segundos "digitando"
    }
    
    try:
        # Log da requisição
        logger.info("\nEnviando mensagem de teste...")
        logger.info(f"Número: {PHONE}")
        logger.info(f"Mensagem: {message}")
        
        # Faz a requisição
        response = requests.post(url, headers=headers, json=payload)
        
        # Log da resposta
        logger.info(f"\nStatus Code: {response.status_code}")
        logger.info(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("\n✅ Mensagem enviada com sucesso!")
            logger.info(f"Z-API ID: {data.get('zaapId')}")
            logger.info(f"Message ID: {data.get('messageId')}")
        else:
            logger.error(f"\n❌ Erro ao enviar mensagem: {response.text}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    send_message() 