import requests
import json
import time
from clint_api.utils.logger import APILogger

logger = APILogger("check_connection")

def check_connection():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    
    # URL base da API
    base_url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}"
    
    # Headers
    headers = {
        "Client-Token": TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Verifica status atual
        logger.info("\nVerificando status da conexão...")
        status_url = f"{base_url}/status"
        status_response = requests.get(status_url, headers=headers)
        
        logger.info(f"Status Code: {status_response.status_code}")
        logger.info(f"Resposta: {status_response.text}")
        
        # 2. Se não estiver conectado, tenta reiniciar
        if "connected" not in status_response.text or "false" in status_response.text.lower():
            logger.info("\nDispositivo não conectado. Tentando reiniciar...")
            
            # Reinicia a conexão
            restart_url = f"{base_url}/restart"
            restart_response = requests.post(restart_url, headers=headers)
            
            logger.info(f"Status Code (Restart): {restart_response.status_code}")
            logger.info(f"Resposta (Restart): {restart_response.text}")
            
            # Aguarda um pouco
            logger.info("\nAguardando 5 segundos...")
            time.sleep(5)
            
            # 3. Tenta obter QR Code
            logger.info("\nSolicitando novo QR Code...")
            qr_url = f"{base_url}/qr-code"
            qr_response = requests.get(qr_url, headers=headers)
            
            logger.info(f"Status Code (QR): {qr_response.status_code}")
            if qr_response.status_code == 200:
                qr_data = qr_response.json()
                if "value" in qr_data:
                    logger.info("\n✅ QR Code obtido com sucesso!")
                    logger.info("\nPara conectar:")
                    logger.info("1. Abra o WhatsApp no seu celular")
                    logger.info("2. Toque em Menu ou Configurações e selecione WhatsApp Web")
                    logger.info("3. Aponte seu celular para este QR Code:")
                    logger.info(f"\n{qr_data['value']}")
                else:
                    logger.error("\n❌ QR Code não disponível na resposta")
            else:
                logger.error(f"\n❌ Erro ao obter QR Code: {qr_response.text}")
        
        logger.info("\nPróximos passos:")
        logger.info("1. Acesse https://app.z-api.io")
        logger.info("2. Localize sua instância")
        logger.info("3. Aguarde o QR Code aparecer")
        logger.info("4. Escaneie o QR Code com o WhatsApp")
        logger.info("5. Use o número 21936182339")
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    check_connection() 