import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebhookHandler:
    def __init__(self, security_token: str):
        self.security_token = security_token
    
    def validate_security_token(self, token: str) -> bool:
        """Validate the security token from the request"""
        return token == self.security_token
    
    def handle_message_status(self, data: Dict[str, Any]) -> None:
        """Handle message status updates"""
        try:
            message_id = data.get('messageId')
            status = data.get('status')
            phone = data.get('phone')
            
            logger.info(f"Message status update - ID: {message_id}, Status: {status}, Phone: {phone}")
            # Add your custom logic here
            
        except Exception as e:
            logger.error(f"Error handling message status: {str(e)}")
    
    def handle_chat_presence(self, data: Dict[str, Any]) -> None:
        """Handle chat presence updates"""
        try:
            phone = data.get('phone')
            presence = data.get('presence', {})
            last_seen = presence.get('lastSeen')
            is_online = presence.get('isOnline')
            
            logger.info(f"Chat presence update - Phone: {phone}, Online: {is_online}, Last seen: {last_seen}")
            # Add your custom logic here
            
        except Exception as e:
            logger.error(f"Error handling chat presence: {str(e)}")
    
    def handle_connection_status(self, data: Dict[str, Any]) -> None:
        """Handle WhatsApp connection status updates"""
        try:
            connected = data.get('connected')
            status = data.get('status')
            
            logger.info(f"Connection status update - Connected: {connected}, Status: {status}")
            # Add your custom logic here
            
        except Exception as e:
            logger.error(f"Error handling connection status: {str(e)}")

# Initialize webhook handler with your security token
webhook_handler = WebhookHandler("your_security_token_here")

@app.post("/webhooks/zapi/message-status")
async def message_status(request: Request, x_api_token: str = Header(None)):
    """Endpoint for message status updates"""
    if not webhook_handler.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    data = await request.json()
    webhook_handler.handle_message_status(data)
    return {"status": "success"}

@app.post("/webhooks/zapi/chat-presence")
async def chat_presence(request: Request, x_api_token: str = Header(None)):
    """Endpoint for chat presence updates"""
    if not webhook_handler.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    data = await request.json()
    webhook_handler.handle_chat_presence(data)
    return {"status": "success"}

@app.post("/webhooks/zapi/connection-status")
async def connection_status(request: Request, x_api_token: str = Header(None)):
    """Endpoint for WhatsApp connection status updates"""
    if not webhook_handler.validate_security_token(x_api_token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    data = await request.json()
    webhook_handler.handle_connection_status(data)
    return {"status": "success"}