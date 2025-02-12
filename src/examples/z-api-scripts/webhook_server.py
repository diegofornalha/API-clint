from fastapi import FastAPI, Request, Header, HTTPException
import uvicorn
import subprocess
import json
import httpx
from typing import Optional, Dict, Any
from clint_api.utils.logger import APILogger

# Configuração do logger
logger = APILogger("webhook_server")

# Criação da aplicação FastAPI
app = FastAPI(title="Z-API Webhook Server")

# Configurações do Z-API
INSTANCE_ID = "3DCAC6407D03208EB32B9A31D728A9CF"
TOKEN = "EF23D3EB62B59971235AC9EF"
SECURITY_TOKEN = "Fd07396a2aa4547d1a45a70acce79a22dS"

# Configuração dos endpoints secundários
SECONDARY_WEBHOOKS = {
    "superagentes": "https://dash.superagentes.ai/api/integrations/whatsapp/webhook?service_provider_id=cm711b30i004jplv79zbrs4z6"
}

async def forward_webhook(url: str, data: Dict[str, Any], event_type: str):
    """Encaminha o webhook para um endpoint secundário"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"Webhook encaminhado para {url}")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
    except Exception as e:
        logger.error(f"Erro ao encaminhar webhook para {url}: {str(e)}")

# Validação do token de segurança
def validate_token(x_api_token: Optional[str] = Header(None)):
    if x_api_token != SECURITY_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")
    return x_api_token

@app.post("/webhooks/zapi/on-send")
async def on_send(request: Request, x_api_token: str = Header(None)):
    """Webhook para mensagens enviadas"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Mensagem enviada: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "on-send")
    
    return {"status": "success"}

@app.post("/webhooks/zapi/on-disconnect")
async def on_disconnect(request: Request, x_api_token: str = Header(None)):
    """Webhook para desconexão"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Desconexão detectada: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "on-disconnect")
    
    return {"status": "success"}

@app.post("/webhooks/zapi/on-receive")
async def on_receive(request: Request, x_api_token: str = Header(None)):
    """Webhook para mensagens recebidas"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Mensagem recebida: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "on-receive")
    
    return {"status": "success"}

@app.post("/webhooks/zapi/on-connect")
async def on_connect(request: Request, x_api_token: str = Header(None)):
    """Webhook para conexão"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Conexão estabelecida: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "on-connect")
    
    return {"status": "success"}

@app.post("/webhooks/zapi/chat-presence")
async def chat_presence(request: Request, x_api_token: str = Header(None)):
    """Webhook para presença no chat"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Presença no chat: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "chat-presence")
    
    return {"status": "success"}

@app.post("/webhooks/zapi/message-status")
async def message_status(request: Request, x_api_token: str = Header(None)):
    """Webhook para status da mensagem"""
    validate_token(x_api_token)
    data = await request.json()
    logger.info(f"Status da mensagem: {json.dumps(data, indent=2)}")
    
    # Encaminha para endpoints secundários
    for name, url in SECONDARY_WEBHOOKS.items():
        await forward_webhook(url, data, "message-status")
    
    return {"status": "success"}

def start_localtunnel(port: int) -> Optional[str]:
    """Inicia o Localtunnel e retorna a URL"""
    try:
        logger.info(f"\nIniciando Localtunnel na porta {port}...")
        tunnel = subprocess.Popen(
            ['lt', '--port', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Aguarda e obtém a URL do tunnel
        for line in tunnel.stdout:
            if "your url is:" in line.lower():
                tunnel_url = line.split("is:")[-1].strip()
                logger.info(f"\n✅ Localtunnel iniciado: {tunnel_url}")
                
                # Log das URLs dos webhooks
                logger.info("\nURLs dos webhooks:")
                logger.info(f"Ao enviar: {tunnel_url}/webhooks/zapi/on-send")
                logger.info(f"Ao desconectar: {tunnel_url}/webhooks/zapi/on-disconnect")
                logger.info(f"Ao receber: {tunnel_url}/webhooks/zapi/on-receive")
                logger.info(f"Ao conectar: {tunnel_url}/webhooks/zapi/on-connect")
                logger.info(f"Presença do chat: {tunnel_url}/webhooks/zapi/chat-presence")
                logger.info(f"Status da mensagem: {tunnel_url}/webhooks/zapi/message-status")
                
                logger.info("\nWebhooks secundários configurados:")
                for name, url in SECONDARY_WEBHOOKS.items():
                    logger.info(f"{name}: {url}")
                
                return tunnel_url
                
    except Exception as e:
        logger.error(f"\n❌ Erro ao iniciar Localtunnel: {str(e)}")
        return None

if __name__ == "__main__":
    PORT = 8001
    tunnel_url = start_localtunnel(PORT)
    
    if tunnel_url:
        logger.info(f"\nIniciando servidor na porta {PORT}...")
        uvicorn.run(app, host="0.0.0.0", port=PORT) 