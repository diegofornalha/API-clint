import requests
from datetime import datetime
from typing import List, Optional, Dict
from ..models.contact import Contato, ContatoStatus, get_session
import os
from dotenv import load_dotenv
import json
from ..utils.logger import APILogger
from ..utils.phone_formatter import PhoneFormatter

logger = APILogger("contact_service")

load_dotenv()

class ContactService:
    def __init__(self):
        self.api_token = os.getenv("CLINT_API_TOKEN")
        self.base_url = "https://api.clint.digital/v1"
        self.session = get_session()
    
    def is_valid_phone(self, phone: str) -> bool:
        """Verifica se o telefone é válido"""
        return PhoneFormatter.is_valid(phone)
    
    def sync_contacts_from_clint(self) -> List[Contato]:
        """Sincroniza contatos da API do Clint com o banco local"""
        headers = {
            "api-token": self.api_token,
            "accept": "application/json"
        }
        
        try:
            logger.info(f"\nFazendo requisição para {self.base_url}/contacts")
            logger.info(f"Token: {self.api_token}")
            
            response = requests.get(
                f"{self.base_url}/contacts",
                headers=headers,
                params={"limit": 1000}  # Ajuste conforme necessário
            )
            
            logger.info(f"\nStatus Code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Processa a resposta JSON
                response_data = response.json()
                logger.info(f"\nRecebidos {len(response_data)} contatos")
                
                # Verifica se a resposta é uma lista ou está dentro de uma chave
                contacts_data = response_data if isinstance(response_data, list) else response_data.get("data", [])
                
                for contact in contacts_data:
                    # Extrai os dados do contato
                    contact_id = str(contact.get("id"))
                    name = contact.get("name", "")
                    full_phone = contact.get("fullPhone", "").replace("+", "")
                    email = contact.get("email", "")
                    
                    # Verifica se o telefone é válido
                    if not self.is_valid_phone(full_phone):
                        logger.info(f"Ignorando contato com telefone inválido: {full_phone}")
                        continue
                    
                    # Formata o telefone para o banco de dados
                    db_phone = PhoneFormatter.format_to_db(full_phone)
                    
                    # Processa as tags (extrai apenas os nomes)
                    tags_data = contact.get("tags", [])
                    tag_names = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
                    
                    logger.info(f"\nProcessando contato:")
                    logger.info(f"ID: {contact_id}")
                    logger.info(f"Nome: {name}")
                    logger.info(f"Telefone: {db_phone}")
                    logger.info(f"Email: {email}")
                    logger.info(f"Tags: {tag_names}")
                    
                    try:
                        # Verifica se o contato já existe
                        existing = self.session.query(Contato).filter_by(
                            clint_id=contact_id
                        ).first()
                        
                        if existing:
                            # Atualiza dados existentes
                            existing.nome = name
                            existing.telefone = db_phone
                            existing.email = email
                            existing.tags = ",".join(tag_names)
                            existing.atualizado_em = datetime.now()
                            logger.info(f"Contato atualizado: {existing}")
                        else:
                            # Verifica se já existe um contato com o mesmo telefone
                            existing_phone = self.session.query(Contato).filter_by(
                                telefone=db_phone
                            ).first()
                            
                            if existing_phone:
                                logger.info(f"Contato com telefone {db_phone} já existe, atualizando...")
                                existing_phone.nome = name
                                existing_phone.email = email
                                existing_phone.tags = ",".join(tag_names)
                                existing_phone.clint_id = contact_id
                                existing_phone.atualizado_em = datetime.now()
                            else:
                                # Cria novo contato
                                novo_contato = Contato(
                                    nome=name,
                                    telefone=db_phone,
                                    email=email,
                                    status=ContatoStatus.INATIVO,
                                    clint_id=contact_id,
                                    tags=",".join(tag_names)
                                )
                                self.session.add(novo_contato)
                                logger.info(f"Novo contato adicionado: {novo_contato}")
                        
                        # Commit a cada contato para evitar perder tudo se houver erro
                        self.session.commit()
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar contato {contact_id}: {str(e)}")
                        self.session.rollback()
                        continue
                
                return self.list_contacts()
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"\nErro detalhado: {str(e)}")
            raise Exception(f"Erro ao sincronizar contatos: {str(e)}")
    
    def list_contacts(self, status: Optional[ContatoStatus] = None) -> List[Contato]:
        """Lista todos os contatos, opcionalmente filtrados por status"""
        query = self.session.query(Contato)
        if status:
            query = query.filter(Contato.status == status)
        return query.all()
    
    def update_contact_status(self, telefone: str, novo_status: ContatoStatus) -> Optional[Contato]:
        """Atualiza o status de um contato"""
        # Formata o telefone para o banco de dados
        db_phone = PhoneFormatter.format_to_db(telefone)
        
        contato = self.session.query(Contato).filter_by(telefone=db_phone).first()
        if contato:
            contato.status = novo_status
            contato.ultima_interacao = datetime.now()
            self.session.commit()
        return contato
    
    def mark_as_active(self, telefone: str) -> Optional[Contato]:
        """Marca um contato como ativo após interação"""
        return self.update_contact_status(telefone, ContatoStatus.ATIVO)
    
    def mark_as_responded(self, telefone: str) -> Optional[Contato]:
        """Marca um contato como respondeu após resposta"""
        return self.update_contact_status(telefone, ContatoStatus.RESPONDEU)
    
    def mark_as_do_not_disturb(self, telefone: str) -> Optional[Contato]:
        """Marca um contato como não perturbe"""
        return self.update_contact_status(telefone, ContatoStatus.NAO_PERTURBE)
    
    def get_inactive_contacts(self) -> List[Contato]:
        """Retorna lista de contatos inativos"""
        return self.list_contacts(ContatoStatus.INATIVO)
    
    def get_active_contacts(self) -> List[Contato]:
        """Retorna lista de contatos ativos"""
        return self.list_contacts(ContatoStatus.ATIVO)
    
    def get_contact_by_phone(self, telefone: str) -> Optional[Contato]:
        """Busca um contato pelo telefone"""
        # Formata o telefone para o banco de dados
        db_phone = PhoneFormatter.format_to_db(telefone)
        return self.session.query(Contato).filter_by(telefone=db_phone).first()

    def send_message(self, contact: Contato, message: str) -> bool:
        """Envia uma mensagem para um contato através da API do Clint"""
        if not contact or not message:
            logger.error("Contato ou mensagem não fornecidos")
            return False
            
        headers = {
            "api-token": self.api_token,
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        # Formata o número de telefone para a API
        api_phone = PhoneFormatter.format_to_api(contact.telefone)
            
        data = {
            "phone": api_phone,
            "text": message,
            "type": "text"
        }
        
        try:
            logger.info(f"Enviando mensagem para {api_phone}")
            logger.info(f"Token: {self.api_token}")
            logger.info(f"Dados: {json.dumps(data)}")
            
            response = requests.post(
                f"{self.base_url}/whatsapp/send",  # Novo endpoint
                headers=headers,
                json=data
            )
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                logger.info("Mensagem enviada com sucesso")
                # Atualiza o status do contato para ativo
                self.mark_as_active(contact.telefone)
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return False 