import requests
import json
from clint_api.utils.logger import APILogger

logger = APILogger("get_qr")

def get_qr_code():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    
    # URL da API para QR Code
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/qr-code"
    
    # Headers
    headers = {
        "Client-Token": TOKEN,
        "Accept": "application/json"
    }
    
    try:
        # Faz a requisição
        logger.info("\nSolicitando QR Code para conexão...")
        response = requests.get(url, headers=headers)
        
        # Log da resposta
        logger.info(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verifica se tem QR Code
            qr_code = data.get("value")
            connected = data.get("connected", False)
            
            if connected:
                logger.info("\n✅ WhatsApp já está conectado!")
            elif qr_code:
                logger.info("\nQR Code obtido com sucesso!")
                logger.info("\nPara conectar:")
                logger.info("1. Abra o WhatsApp no seu celular")
                logger.info("2. Toque em Menu ou Configurações e selecione WhatsApp Web")
                logger.info("3. Aponte seu celular para o QR Code")
                logger.info(f"\nQR Code: {qr_code}")
            else:
                logger.error("\n❌ QR Code não disponível")
                
        else:
            logger.error(f"\n❌ Erro ao solicitar QR Code: {response.text}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    get_qr_code() 