from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class MessageType(Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"

@dataclass
class WhatsAppMessage:
    """Modelo de dados para mensagens do WhatsApp"""
    phone: str
    message: str
    instance_id: str
    token: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    caption: Optional[str] = None
    message_id: Optional[str] = None
    status: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a mensagem para dicionário"""
        data = {
            "phone": self.phone
        }
        
        if self.message_type == MessageType.TEXT:
            data["message"] = self.message
        else:
            data["url"] = self.media_url
            if self.caption:
                data["caption"] = self.caption
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], instance_id: str, token: str) -> 'WhatsAppMessage':
        """Cria uma instância de WhatsAppMessage a partir de um dicionário"""
        message_type = MessageType.TEXT
        message = data.get("message", "")
        media_url = None
        caption = None
        
        if "url" in data:
            media_url = data["url"]
            caption = data.get("caption")
            message = caption or ""
            # Determina o tipo de mídia pela extensão ou content-type
            if media_url:
                if any(ext in media_url.lower() for ext in [".jpg", ".jpeg", ".png"]):
                    message_type = MessageType.IMAGE
                elif any(ext in media_url.lower() for ext in [".mp3", ".ogg", ".wav"]):
                    message_type = MessageType.AUDIO
                elif any(ext in media_url.lower() for ext in [".mp4", ".avi", ".mov"]):
                    message_type = MessageType.VIDEO
                else:
                    message_type = MessageType.DOCUMENT
        
        return cls(
            phone=data["phone"],
            message=message,
            instance_id=instance_id,
            token=token,
            message_type=message_type,
            media_url=media_url,
            caption=caption,
            message_id=data.get("messageId"),
            status=data.get("status")
        ) 