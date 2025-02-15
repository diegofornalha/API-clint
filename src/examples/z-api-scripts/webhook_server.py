from fastapi import FastAPI, Request
from clint_api.utils.logger import APILogger
from clint_api.services.message_history_service import MessageHistoryService
import uvicorn
import json
import time
from datetime import datetime

# Configura o logger
logger = APILogger("webhook_server")

# Inicializa serviços
history_service = MessageHistoryService()

# Cria a aplicação FastAPI
app = FastAPI(title="Z-API Webhook Server")

# Dicionário para armazenar eventos recebidos
events = {
    "on-send": [],
    "on-disconnect": [],
    "on-receive": [],
    "chat-presence": [],
    "message-status": [],
    "on-connect": []
}

def log_event(event_type: str, data: dict):
    """Registra um evento no log e no dicionário de eventos"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    events[event_type].append({
        "timestamp": timestamp,
        "data": data
    })
    
    # Mantém apenas os últimos 100 eventos de cada tipo
    if len(events[event_type]) > 100:
        events[event_type].pop(0)
    
    # Log do evento
    logger.info(f"\n📥 Evento {event_type} recebido em {timestamp}")
    logger.info(f"Payload: {json.dumps(data, indent=2)}")

@app.get("/")
async def root():
    """Endpoint de status do servidor"""
    return {
        "status": "online",
        "timestamp": time.time(),
        "events_received": {
            event_type: len(events) for event_type, events in events.items()
        }
    }

@app.post("/webhooks/zapi/on-send")
async def webhook_on_send(request: Request):
    """Webhook para mensagens enviadas"""
    data = await request.json()
    log_event("on-send", data)
    return {"status": "received"}

@app.post("/webhooks/zapi/on-disconnect")
async def webhook_on_disconnect(request: Request):
    """Webhook para desconexões"""
    data = await request.json()
    log_event("on-disconnect", data)
    return {"status": "received"}

@app.post("/webhooks/zapi/test")
async def webhook_test(request: Request):
    """Endpoint de teste para validar webhook"""
    try:
        data = await request.json()
        logger.info("\n🔍 Teste de webhook recebido")
        logger.info(f"Headers: {request.headers}")
        logger.info(f"Payload: {json.dumps(data, indent=2)}")
        return {"status": "success", "message": "Webhook test received"}
    except Exception as e:
        logger.error(f"❌ Erro no teste do webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/zapi/on-receive")
async def webhook_on_receive(request: Request):
    """Webhook para mensagens recebidas"""
    try:
        # Validação do Client-Token
        client_token = request.headers.get("Client-Token")
        if not client_token:
            logger.error("❌ Client-Token não encontrado nos headers")
            return {"status": "error", "message": "Client-Token is required"}
            
        # Log detalhado da requisição
        logger.info("\n🔍 Nova requisição recebida no webhook on-receive")
        logger.info("\nHeaders da requisição:")
        for header, value in request.headers.items():
            logger.info(f"{header}: {value}")
        
        # Log do corpo da requisição bruto
        body = await request.body()
        logger.info(f"\n📦 Corpo da requisição bruto: {body.decode()}")
        
        data = await request.json()
        logger.info(f"\n📥 Payload processado: {json.dumps(data, indent=2)}")
        
        # Registra o evento
        log_event("on-receive", data)
        
        # Registra a mensagem no histórico independente de quem enviou
        try:
            # Extrai a mensagem do payload
            message = ""
            message_type = "text"
            media_url = None
            
            # Verifica o tipo de mensagem e extrai o conteúdo
            if "text" in data:
                if isinstance(data["text"], dict):
                    message = data["text"].get("message", "")
                else:
                    message = str(data["text"])
                logger.info(f"Mensagem de texto extraída: {message}")
            elif "image" in data:
                message = f"[Imagem] {data['image'].get('caption', '')}"
                message_type = "image"
                media_url = data['image'].get('imageUrl')
                logger.info(f"Mensagem de imagem extraída: {message}, URL: {media_url}")
            elif "video" in data:
                message = f"[Vídeo] {data['video'].get('caption', '')}"
                message_type = "video"
                media_url = data['video'].get('videoUrl')
                logger.info(f"Mensagem de vídeo extraída: {message}, URL: {media_url}")
            elif "audio" in data:
                message = "[Áudio]"
                message_type = "audio"
                media_url = data['audio'].get('audioUrl')
                logger.info(f"Mensagem de áudio extraída: URL: {media_url}")
            elif "document" in data:
                message = f"[Documento] {data['document'].get('fileName', '')}"
                message_type = "document"
                media_url = data['document'].get('documentUrl')
                logger.info(f"Mensagem de documento extraída: {message}, URL: {media_url}")
            
            # Verifica se conseguiu extrair a mensagem
            if not message and not media_url:
                logger.warning("Não foi possível extrair a mensagem do payload")
                logger.warning(f"Payload recebido: {json.dumps(data, indent=2)}")
                return {"status": "error", "message": "Mensagem não encontrada no payload"}
            
            # Cria o objeto de histórico
            history_item = {
                "message_id": data.get("messageId"),
                "phone": data.get("phone"),
                "direction": "RECEIVED",
                "message": message,
                "message_type": message_type,
                "status": "received",
                "media_url": media_url,
                "timestamp": datetime.fromtimestamp(data.get("momment", time.time() * 1000) / 1000)
            }
            
            # Registra no histórico
            result = history_service.add_received_message(data)
            
            if result:
                logger.info("✅ Mensagem registrada no histórico com sucesso")
                logger.info(f"Detalhes da mensagem: {json.dumps(history_item, indent=2, default=str)}")
            else:
                logger.error("❌ Falha ao registrar mensagem no histórico")
            
            return {"status": "received", "message": "Mensagem processada com sucesso"}
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar mensagem no histórico: {str(e)}")
            logger.error(f"Dados da mensagem que causou erro: {json.dumps(data, indent=2)}")
            return {"status": "error", "message": f"Erro ao processar mensagem: {str(e)}"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook on-receive: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/zapi/chat-presence")
async def webhook_chat_presence(request: Request):
    """Webhook para presença no chat"""
    data = await request.json()
    log_event("chat-presence", data)
    return {"status": "received"}

@app.post("/webhooks/zapi/message-status")
async def webhook_message_status(request: Request):
    """Webhook para status de mensagens"""
    data = await request.json()
    log_event("message-status", data)
    
    # Atualiza o status da mensagem no histórico
    try:
        message_id = data.get("messageId")
        status = data.get("status")
        if message_id and status:
            history_service.update_message_status(message_id, status)
    except Exception as e:
        logger.error(f"Erro ao atualizar status da mensagem no histórico: {str(e)}")
    
    return {"status": "received"}

@app.post("/webhooks/zapi/on-connect")
async def webhook_on_connect(request: Request):
    """Webhook para conexões"""
    data = await request.json()
    log_event("on-connect", data)
    return {"status": "received"}

@app.get("/events/{event_type}")
async def get_events(event_type: str):
    """Retorna os eventos armazenados de um determinado tipo"""
    if event_type not in events:
        return {"error": "Tipo de evento inválido"}
    return {
        "event_type": event_type,
        "count": len(events[event_type]),
        "events": events[event_type]
    }

@app.get("/events")
async def get_all_events():
    """Retorna todos os eventos armazenados"""
    return events

@app.post("/webhook-test/zapi")
async def webhook_handler(request: Request):
    """Endpoint unificado para todos os webhooks do Z-API"""
    try:
        # Validação do Client-Token
        client_token = request.headers.get("Client-Token")
        if not client_token:
            logger.error("❌ Client-Token não encontrado nos headers")
            return {"status": "error", "message": "Client-Token is required"}
        elif client_token != "Fd07396a2aa4547d1a45a70acce79a22dS":
            logger.error("❌ Client-Token inválido")
            return {"status": "error", "message": "Invalid Client-Token"}
            
        # Log detalhado da requisição
        logger.info("\n🔍 Nova requisição recebida no webhook")
        logger.info("\nHeaders da requisição:")
        for header, value in request.headers.items():
            logger.info(f"{header}: {value}")
        
        # Log do corpo da requisição bruto
        body = await request.body()
        logger.info(f"\n📦 Corpo da requisição bruto: {body.decode()}")
        
        data = await request.json()
        logger.info(f"\n📥 Payload processado: {json.dumps(data, indent=2)}")
        
        # Extrai dados do corpo da requisição
        body_data = data.get("body", {})
        phone = body_data.get("phone", "")
        message = data.get("message", "")
        option_list = data.get("optionList", {})
        
        # Prepara a resposta no formato especificado
        response = {
            "waitingMessage": data.get("waitingMessage", False),
            "isEdit": data.get("isEdit", False),
            "isGroup": data.get("isGroup", False),
            "isNewsletter": data.get("isNewsletter", False),
            "instanceId": "3DCC625CC314A038C87896155CBF9532",
            "messageId": data.get("messageId", ""),
            "phone": phone,
            "fromMe": data.get("fromMe", False),
            "momment": int(time.time() * 1000),
            "status": "RECEIVED",
            "chatName": data.get("chatName", ""),
            "senderPhoto": data.get("senderPhoto"),
            "senderName": data.get("senderName", ""),
            "photo": data.get("photo"),
            "broadcast": data.get("broadcast", False),
            "participantLid": data.get("participantLid"),
            "forwarded": data.get("forwarded", False),
            "type": "ReceivedCallback",
            "fromApi": data.get("fromApi", False),
            "text": {
                "message": message
            },
            "webhookUrl": "https://xfxacademy.app.n8n.cloud/webhook-test/zapi",
            "executionMode": "test"
        }
        
        # Se houver optionList, adiciona ao response
        if option_list:
            response["optionList"] = option_list
        
        # Loga os campos para debug
        for key, value in response.items():
            if key != "text":
                logger.info(f"{key}: {value}")
        if "text" in response:
            logger.info(f"text.message: {response['text'].get('message')}")
        
        # Registra o evento como mensagem recebida
        log_event("on-receive", response)
        
        # Registra no histórico
        result = history_service.add_received_message(response)
        if result:
            logger.info("✅ Mensagem registrada no histórico com sucesso")
        else:
            logger.error("❌ Falha ao registrar mensagem no histórico")
        
        # Retorna a resposta no formato especificado
        return response
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/webhook-test/n8n")
async def webhook_n8n_handler(request: Request):
    """Endpoint para receber webhooks do n8n e repassar para o endpoint principal"""
    try:
        # Log detalhado da requisição do n8n
        logger.info("\n🔄 Requisição recebida do n8n")
        logger.info("\nHeaders da requisição:")
        for header, value in request.headers.items():
            logger.info(f"{header}: {value}")
        
        # Log do corpo da requisição bruto
        body = await request.body()
        logger.info(f"\n📦 Corpo da requisição do n8n: {body.decode()}")
        
        data = await request.json()
        logger.info(f"\n📥 Payload do n8n processado: {json.dumps(data, indent=2)}")
        
        # Extrai e loga todos os campos relevantes
        logger.info("\n📝 Detalhes da mensagem recebida do n8n:")
        logger.info(f"waitingMessage: {data.get('waitingMessage', False)}")
        logger.info(f"isEdit: {data.get('isEdit', False)}")
        logger.info(f"isGroup: {data.get('isGroup', False)}")
        logger.info(f"isNewsletter: {data.get('isNewsletter', False)}")
        logger.info(f"instanceId: {data.get('instanceId')}")
        logger.info(f"messageId: {data.get('messageId')}")
        logger.info(f"phone: {data.get('phone')}")
        logger.info(f"fromMe: {data.get('fromMe', False)}")
        logger.info(f"momment: {data.get('momment')}")
        logger.info(f"status: {data.get('status')}")
        logger.info(f"chatName: {data.get('chatName')}")
        logger.info(f"senderPhoto: {data.get('senderPhoto')}")
        logger.info(f"senderName: {data.get('senderName')}")
        logger.info(f"photo: {data.get('photo')}")
        logger.info(f"broadcast: {data.get('broadcast', False)}")
        logger.info(f"participantLid: {data.get('participantLid')}")
        logger.info(f"forwarded: {data.get('forwarded', False)}")
        
        if "text" in data:
            logger.info(f"text.message: {data['text'].get('message')}")
        
        # Registra o evento
        log_event("on-receive", data)
        
        # Processa a mensagem no histórico
        result = history_service.add_received_message(data)
        if result:
            logger.info("✅ Mensagem do n8n registrada no histórico com sucesso")
            logger.info(f"Detalhes: ID={result.message_id}, Tipo=text, Mensagem={data.get('text', {}).get('message')}")
        else:
            logger.error("❌ Falha ao registrar mensagem do n8n no histórico")
        
        return {"status": "received", "source": "n8n"}
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook do n8n: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)
        return {"status": "error", "message": str(e)}

def main():
    """Inicia o servidor"""
    logger.info("\n🚀 Iniciando servidor de webhooks...")
    logger.info("\nEndpoints disponíveis:")
    logger.info("GET  / - Status do servidor")
    logger.info("GET  /events/{event_type} - Lista eventos de um tipo")
    logger.info("GET  /events - Lista todos os eventos")
    logger.info("POST /webhooks/zapi/on-send - Webhook de mensagens enviadas")
    logger.info("POST /webhooks/zapi/on-disconnect - Webhook de desconexão")
    logger.info("POST /webhooks/zapi/test - Webhook de teste")
    logger.info("POST /webhooks/zapi/on-receive - Webhook de mensagens recebidas")
    logger.info("POST /webhooks/zapi/chat-presence - Webhook de presença no chat")
    logger.info("POST /webhooks/zapi/message-status - Webhook de status de mensagens")
    logger.info("POST /webhooks/zapi/on-connect - Webhook de conexão")
    
    # Inicia o servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main() 