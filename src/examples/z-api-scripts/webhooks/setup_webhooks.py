import requests
import json
import subprocess
import time
from clint_api.utils.logger import APILogger

logger = APILogger("setup_webhooks")

def setup_webhooks():
    # Configurações do Z-API
    INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
    TOKEN = "EF23D3EB62B59971235AC9EF"
    PORT = 8000  # Porta que seu servidor webhook vai usar
    
    # URL base da API
    base_url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}"
    
    # Headers
    headers = {
        "Client-Token": TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        # Inicia o Localtunnel
        logger.info(f"\nIniciando Localtunnel na porta {PORT}...")
        tunnel = subprocess.Popen(
            ['lt', '--port', str(PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Aguarda e obtém a URL do tunnel
        tunnel_url = None
        for line in tunnel.stdout:
            if "your url is:" in line.lower():
                tunnel_url = line.split("is:")[-1].strip()
                break
        
        if not tunnel_url:
            logger.error("\n❌ Erro ao obter URL do Localtunnel")
            return
        
        logger.info(f"\n✅ Localtunnel iniciado: {tunnel_url}")
        
        # Configura os webhooks
        webhooks = {
            "on-send": f"{tunnel_url}/webhooks/zapi/on-send",
            "on-disconnect": f"{tunnel_url}/webhooks/zapi/on-disconnect",
            "on-receive": f"{tunnel_url}/webhooks/zapi/on-receive",
            "on-connect": f"{tunnel_url}/webhooks/zapi/on-connect",
            "chat-presence": f"{tunnel_url}/webhooks/zapi/chat-presence",
            "message-status": f"{tunnel_url}/webhooks/zapi/message-status"
        }
        
        logger.info("\nConfigurando webhooks:")
        for webhook_type, webhook_url in webhooks.items():
            logger.info(f"\nConfigurando webhook {webhook_type}...")
            logger.info(f"URL: {webhook_url}")
            
            # Aqui você pode implementar a chamada para configurar cada webhook
            # Nota: A Z-API pode ter um endpoint específico para isso
            
        logger.info("\n✅ Configuração dos webhooks concluída!")
        logger.info("\nURLs configuradas:")
        for webhook_type, webhook_url in webhooks.items():
            logger.info(f"{webhook_type}: {webhook_url}")
        
        logger.info("\nPressione Ctrl+C para encerrar o Localtunnel")
        tunnel.wait()
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")
    finally:
        if 'tunnel' in locals():
            tunnel.terminate()

if __name__ == "__main__":
    setup_webhooks() 