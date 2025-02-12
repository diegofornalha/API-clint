import requests
import json
import time
from clint_api.utils.logger import APILogger

logger = APILogger("restart_connection")

def restart_connection():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    
    # URL da API v2 para restart
    url = f"https://api.z-api.io/v2/instances/{INSTANCE_ID}/token/{TOKEN}/restart"
    
    # Headers
    headers = {
        "Client-Token": TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        # Faz a requisição de restart
        logger.info("\nReiniciando conexão do WhatsApp...")
        response = requests.post(url, headers=headers, json={})
        
        # Log da resposta
        logger.info(f"\nStatus Code: {response.status_code}")
        logger.info(f"Resposta: {response.text}")
        
        if response.status_code in [200, 201]:
            logger.info("\n✅ Comando de reinicialização enviado com sucesso!")
            logger.info("\nAguardando 10 segundos para a reinicialização...")
            time.sleep(10)
            
            # Verifica o status após o restart
            status_url = f"https://api.z-api.io/v2/instances/{INSTANCE_ID}/token/{TOKEN}/connection"
            status_response = requests.get(status_url, headers=headers)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                logger.info(f"\nStatus após reinicialização: {json.dumps(status_data, indent=2)}")
                
                logger.info("\nPróximos passos:")
                logger.info("1. Acesse https://app.z-api.io")
                logger.info("2. Localize sua instância")
                logger.info("3. Aguarde o QR Code aparecer")
                logger.info("4. Escaneie o QR Code com o WhatsApp")
                logger.info("5. Use o número 21936182339")
            else:
                logger.error(f"\n❌ Erro ao verificar status após reinicialização: {status_response.text}")
        else:
            logger.error(f"\n❌ Erro ao reiniciar conexão: {response.text}")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    restart_connection() 