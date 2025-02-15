from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
import os

Base = declarative_base()

class MessageDirection(enum.Enum):
    """Direção da mensagem"""
    SENT = "sent"
    RECEIVED = "received"

class MessageHistory(Base):
    """Modelo para histórico de mensagens"""
    __tablename__ = 'message_history'

    id = Column(Integer, primary_key=True)
    message_id = Column(String(100))  # ID da mensagem no Z-API
    phone = Column(String(20))  # Número do telefone
    direction = Column(Enum(MessageDirection))  # Enviada ou recebida
    message = Column(Text)  # Conteúdo da mensagem
    message_type = Column(String(20))  # Tipo da mensagem (texto, imagem, etc)
    status = Column(String(20))  # Status da mensagem
    media_url = Column(String(500), nullable=True)  # URL da mídia (se houver)
    timestamp = Column(DateTime, default=datetime.now)  # Data/hora da mensagem
    
    def __repr__(self):
        return f"<MessageHistory(phone='{self.phone}', direction='{self.direction.value}', timestamp='{self.timestamp}')>"

def init_message_history_db():
    """Inicializa o banco de dados de histórico de mensagens"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'message_history.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session() 