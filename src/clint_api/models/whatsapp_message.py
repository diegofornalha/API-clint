from enum import Enum
from typing import Optional

class MessageType(Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    LINK = "link"

class WhatsAppMessage:
    """Modelo para mensagens do WhatsApp"""
    
    def __init__(
        self,
        phone: str,
        message: str,
        message_type: MessageType = MessageType.TEXT,
        media_url: Optional[str] = None,
        caption: Optional[str] = None,
        instance_id: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Inicializa uma nova mensagem
        
        Args:
            phone: Número do destinatário
            message: Conteúdo da mensagem
            message_type: Tipo da mensagem (texto, imagem, etc)
            media_url: URL da mídia (para mensagens com mídia)
            caption: Legenda da mídia
            instance_id: ID da instância (opcional)
            token: Token da API (opcional)
        """
        self.phone = phone
        self.message = message
        self.message_type = message_type
        self.media_url = media_url
        self.caption = caption
        self.instance_id = instance_id
        self.token = token
        self.message_id = None
        self.status = "pending"
    
    def to_dict(self) -> dict:
        """Converte a mensagem para dicionário"""
        data = {
            "phone": self.phone,
            "message": self.message,
            "messageType": self.message_type.value
        }
        
        if self.media_url:
            data["mediaUrl"] = self.media_url
            
        if self.caption:
            data["caption"] = self.caption
            
        if self.instance_id:
            data["instanceId"] = self.instance_id
            
        if self.token:
            data["token"] = self.token
            
        if self.message_id:
            data["messageId"] = self.message_id
            
        if self.status:
            data["status"] = self.status
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "WhatsAppMessage":
        """
        Cria uma mensagem a partir de um dicionário
        
        Args:
            data: Dicionário com os dados da mensagem
            
        Returns:
            Nova instância de WhatsAppMessage
        """
        return cls(
            phone=data.get("phone"),
            message=data.get("message"),
            message_type=MessageType(data.get("messageType", "text")),
            media_url=data.get("mediaUrl"),
            caption=data.get("caption"),
            instance_id=data.get("instanceId"),
            token=data.get("token")
        ) 