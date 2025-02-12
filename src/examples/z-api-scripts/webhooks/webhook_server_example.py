from fastapi import FastAPI, Request, Header, HTTPException
from clint_api.services.webhook_service import WebhookService
from clint_api.utils.logger import APILogger
from clint_api.utils.config import Config
import subprocess
import sys

app = FastAPI()
webhook_service = WebhookService()
logger = APILogger("webhook_server")

@app.post("/webhooks/zapi/on-receive")
async def on_receive(request: Request, x_api_token: str = Header(None)):
    """Endpoint para receber mensagens"""
    if not webhook_service.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    data = await request.json()
    webhook_service.process_message_received(data)
    return {"status": "success"}

@app.post("/webhooks/zapi/on-send")
async def on_send(request: Request, x_api_token: str = Header(None)):
    """Endpoint para mensagens enviadas"""
    if not webhook_service.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    data = await request.json()
    webhook_service.process_message_received(data)  # Reusa o mesmo processamento
    return {"status": "success"}

@app.post("/webhooks/zapi/message-status")
async def message_status(request: Request, x_api_token: str = Header(None)):
    """Endpoint para status de mensagens"""
    if not webhook_service.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    data = await request.json()
    webhook_service.process_message_status(data)
    return {"status": "success"}

@app.post("/webhooks/zapi/on-connect")
@app.post("/webhooks/zapi/on-disconnect")
async def connection_status(request: Request, x_api_token: str = Header(None)):
    """Endpoint para status de conexão"""
    if not webhook_service.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    data = await request.json()
    webhook_service.process_connection_status(data)
    return {"status": "success"}

@app.post("/webhooks/zapi/chat-presence")
async def chat_presence(request: Request, x_api_token: str = Header(None)):
    """Endpoint para presença no chat"""
    if not webhook_service.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    data = await request.json()
    webhook_service.process_chat_presence(data)
    return {"status": "success"}

if __name__ == "__main__":
    PORT = 8001
    logger.info(f"\nIniciando servidor webhook na porta {PORT}...")
    
    # Inicia o Localtunnel em background
    try:
        tunnel = subprocess.Popen(['lt', '--port', str(PORT)], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
        
        # Lê a primeira linha que contém a URL
        for line in tunnel.stdout:
            if "your url is:" in line.lower():
                url = line.split("is:")[-1].strip()
                logger.info(f"\nSua URL pública é: {url}")
                logger.info("Use esta URL para configurar os webhooks no Z-API")
                break
    except FileNotFoundError:
        logger.error("Localtunnel não encontrado. Instale com: npm install -g localtunnel")
        sys.exit(1)
    
    # Inicia o servidor
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT) 