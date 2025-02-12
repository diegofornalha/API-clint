import requests
import json
from clint_api.utils.logger import APILogger

logger = APILogger("check_status")

def check_connection_status():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    
    # URL da API (v2)
    url = f"https://api.z-api.io/v2/instances/{INSTANCE_ID}/token/{TOKEN}/connection"
    
    # Headers
    headers = {
        "Client-Token": TOKEN,
        "Accept": "application/json"
    }
    
    try:
        # Faz a requisição
        logger.info("\nVerificando status detalhado da conexão...")
        response = requests.get(url, headers=headers)
        
        # Log da resposta completa
        logger.info(f"\nStatus Code: {response.status_code}")
        logger.info(f"Headers da resposta: {dict(response.headers)}")
        logger.info(f"Resposta completa: {json.dumps(response.json(), indent=2)}")
        
        # Analisa a resposta
        if response.status_code == 200:
            data = response.json()
            
            # Verifica os detalhes do status
            connected = data.get("connected", False)
            status = data.get("status", "N/A")
            
            logger.info("\nDetalhes da conexão:")
            logger.info(f"Conectado: {'✅ Sim' if connected else '❌ Não'}")
            logger.info(f"Status: {status}")
            
            if not connected:
                logger.info("\nPara conectar:")
                logger.info("1. Acesse https://app.z-api.io")
                logger.info("2. Localize sua instância")
                logger.info("3. Escaneie o QR Code com o WhatsApp")
                logger.info("4. Use o número 21936182339")
        else:
            logger.error(f"\n❌ Erro ao verificar status: {response.text}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro ao verificar status: {str(e)}")

if __name__ == "__main__":
    check_connection_status() 