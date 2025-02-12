from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
import os

Base = declarative_base()

class ContatoStatus(enum.Enum):
    INATIVO = "inativo"
    ATIVO = "ativo"
    RESPONDEU = "respondeu"
    NAO_PERTURBE = "nao_perturbe"
    REMOVIDO = "removido"

class Contato(Base):
    __tablename__ = 'contatos'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    telefone = Column(String(20), unique=True)
    email = Column(String(100))
    status = Column(Enum(ContatoStatus), default=ContatoStatus.INATIVO)
    ultima_interacao = Column(DateTime)
    tags = Column(String(200))  # Tags separadas por vírgula
    clint_id = Column(String(50))  # ID do contato na API do Clint
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Contato(nome='{self.nome}', telefone='{self.telefone}', status='{self.status.value}')>"

def init_db():
    """Inicializa o banco de dados"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'contatos.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()

def get_session():
    """Retorna uma nova sessão do banco de dados"""
    return init_db() 