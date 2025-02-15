from typing import List, Optional
from datetime import datetime
from ..models.message_history import MessageHistory, MessageDirection, init_message_history_db
from ..models.whatsapp_message import WhatsAppMessage
from ..utils.logger import APILogger
import json

logger = APILogger("message_history")

class MessageHistoryService:
    """Serviço para gerenciar histórico de mensagens"""
    
    def __init__(self):
        self.session = init_message_history_db()
    
    def add_sent_message(self, message: WhatsAppMessage) -> MessageHistory:
        """
        Adiciona uma mensagem enviada ao histórico
        
        Args:
            message: Mensagem enviada
            
        Returns:
            Registro do histórico
        """
        history = MessageHistory(
            message_id=message.message_id,
            phone=message.phone,
            direction=MessageDirection.SENT,
            message=message.message,
            message_type=message.message_type.value,
            status=message.status,
            media_url=message.media_url,
            timestamp=datetime.now()
        )
        
        try:
            self.session.add(history)
            self.session.commit()
            logger.info(f"Mensagem enviada registrada no histórico: {history}")
            return history
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro ao registrar mensagem enviada: {str(e)}")
            raise
    
    def add_received_message(self, data: dict) -> MessageHistory:
        """
        Adiciona uma mensagem recebida ao histórico
        
        Args:
            data: Dados do webhook de mensagem recebida
            
        Returns:
            Registro do histórico
        """
        try:
            # Log do payload recebido para debug
            logger.info(f"\n📥 Processando mensagem recebida")
            logger.info(f"Payload: {json.dumps(data, indent=2)}")
            
            # Extrai a mensagem do texto ou de outros tipos de mídia
            message = ""
            message_type = "text"
            media_url = None
            
            # Verifica se é uma mensagem de texto direta
            if isinstance(data.get("text"), str):
                message = data.get("text", "")
                logger.info(f"Mensagem de texto direta: {message}")
            # Verifica se é uma mensagem de texto no formato objeto
            elif isinstance(data.get("text"), dict):
                message = data.get("text", {}).get("message", "")
                logger.info(f"Mensagem de texto em objeto: {message}")
            # Verifica se é um template
            elif "hydratedTemplate" in data:
                message = data.get("hydratedTemplate", {}).get("message", "")
                message_type = "template"
                logger.info(f"Mensagem de template: {message}")
            # Outros tipos de mídia
            elif "image" in data:
                message = data.get("image", {}).get("caption", "")
                message_type = "image"
                media_url = data.get("image", {}).get("imageUrl")
                logger.info(f"Mensagem de imagem: caption={message}, url={media_url}")
            elif "video" in data:
                message = data.get("video", {}).get("caption", "")
                message_type = "video"
                media_url = data.get("video", {}).get("videoUrl")
                logger.info(f"Mensagem de vídeo: caption={message}, url={media_url}")
            elif "audio" in data:
                message = "[Áudio]"
                message_type = "audio"
                media_url = data.get("audio", {}).get("audioUrl")
                logger.info(f"Mensagem de áudio: url={media_url}")
            elif "document" in data:
                message = f"[Documento] {data.get('document', {}).get('fileName', '')}"
                message_type = "document"
                media_url = data.get("document", {}).get("documentUrl")
                logger.info(f"Mensagem de documento: name={message}, url={media_url}")
            
            # Se nenhum tipo específico foi encontrado, tenta extrair a mensagem do campo text
            if not message and data.get("text"):
                message = data.get("text")
                if isinstance(message, dict):
                    message = message.get("message", "")
            
            # Log dos dados extraídos
            logger.info(f"\n📝 Dados extraídos:")
            logger.info(f"Mensagem: {message}")
            logger.info(f"Tipo: {message_type}")
            logger.info(f"URL da mídia: {media_url}")
            
            # Verifica se a mensagem não é vazia
            if not message and not media_url:
                logger.warning("⚠️ Mensagem vazia recebida")
                logger.warning(f"Payload: {json.dumps(data, indent=2)}")
                return None
            
            # Cria o registro no histórico
            history = MessageHistory(
                message_id=data.get("messageId"),
                phone=data.get("phone"),
                direction=MessageDirection.RECEIVED,
                message=message,
                message_type=message_type,
                status="received",
                media_url=media_url,
                timestamp=datetime.fromtimestamp(data.get("momment", 0) / 1000) if data.get("momment") else datetime.now()
            )
            
            # Adiciona e salva no banco
            self.session.add(history)
            self.session.commit()
            logger.info(f"\n✅ Mensagem registrada no histórico:")
            logger.info(f"ID: {history.message_id}")
            logger.info(f"Telefone: {history.phone}")
            logger.info(f"Mensagem: {history.message}")
            logger.info(f"Tipo: {history.message_type}")
            logger.info(f"Status: {history.status}")
            logger.info(f"Timestamp: {history.timestamp}")
            
            return history
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"\n❌ Erro ao registrar mensagem recebida: {str(e)}")
            logger.error(f"Dados que causaram erro: {json.dumps(data, indent=2)}")
            raise
    
    def get_chat_history(self, phone: str, limit: int = 100) -> List[MessageHistory]:
        """
        Obtém histórico de mensagens de um número
        
        Args:
            phone: Número do telefone
            limit: Limite de mensagens (padrão: 100)
            
        Returns:
            Lista de mensagens ordenadas por data
        """
        try:
            history = self.session.query(MessageHistory)\
                .filter(MessageHistory.phone == phone)\
                .order_by(MessageHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            logger.info(f"Histórico obtido para {phone}: {len(history)} mensagens")
            return history
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {str(e)}")
            return []
    
    def update_message_status(self, message_id: str, new_status: str) -> Optional[MessageHistory]:
        """
        Atualiza o status de uma mensagem
        
        Args:
            message_id: ID da mensagem
            new_status: Novo status
            
        Returns:
            Registro atualizado ou None se não encontrado
        """
        try:
            message = self.session.query(MessageHistory)\
                .filter(MessageHistory.message_id == message_id)\
                .first()
            
            if message:
                message.status = new_status
                self.session.commit()
                logger.info(f"Status da mensagem {message_id} atualizado para {new_status}")
                return message
            else:
                logger.warning(f"Mensagem {message_id} não encontrada para atualização de status")
                return None
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro ao atualizar status da mensagem: {str(e)}")
            return None
    
    def clear_chat_history(self, phone: str = None) -> bool:
        """
        Limpa o histórico de mensagens
        
        Args:
            phone: Número do telefone (opcional). Se não fornecido, limpa todo o histórico
            
        Returns:
            True se a operação foi bem sucedida, False caso contrário
        """
        try:
            query = self.session.query(MessageHistory)
            if phone:
                query = query.filter(MessageHistory.phone == phone)
            
            query.delete()
            self.session.commit()
            
            if phone:
                logger.info(f"Histórico limpo para o número {phone}")
            else:
                logger.info("Todo o histórico foi limpo")
            
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro ao limpar histórico: {str(e)}")
            return False 