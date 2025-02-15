import requests
import json
import time
from typing import Dict, Any, Optional

from ..models.whatsapp_message import WhatsAppMessage, MessageType
from ..exceptions.api_exceptions import APIAuthenticationError, ClintAPIException
from ..utils.decorators import retry, log_api_call
from ..utils.logger import APILogger
from ..services.contact_service import ContactService
from ..utils.phone_formatter import PhoneFormatter

logger = APILogger("zapi_client")

class ZAPIClient:
    """Cliente para integração com a Z-API"""
    
    def __init__(self, instance_id: str, token: str, security_token: str = "Fd07396a2aa4547d1a45a70acce79a22dS"):
        self.instance_id = instance_id
        self.token = token
        self.security_token = security_token
        self.base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        self.headers = {
            "Client-Token": security_token,
            "Content-Type": "application/json"
        }
        self.contact_service = ContactService()
    
    def _get_url(self, endpoint: str) -> str:
        """Constrói a URL completa para o endpoint"""
        return f"{self.base_url}/{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Processa a resposta da API e trata erros"""
        try:
            if response.status_code == 401:
                raise APIAuthenticationError("Token ou Instance ID inválidos")
            elif response.status_code not in [200, 201, 202]:
                raise ClintAPIException(f"Erro na API Z-API: {response.text}")
            
            return response.json() if response.text else {}
        except ValueError as e:
            raise ClintAPIException(f"Resposta inválida da API: {str(e)}")
    
    @retry(max_attempts=3, delay=1.0)
    @log_api_call("zapi_restart_connection")
    def restart_connection(self) -> bool:
        """Reinicia a conexão com o WhatsApp"""
        url = self._get_url("restart")
        
        try:
            logger.info("Reiniciando conexão com o WhatsApp...")
            response = requests.post(url, headers=self.headers)
            
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Resposta: {response.text}")
            
            if response.status_code in [200, 201]:
                logger.info("Conexão reiniciada com sucesso!")
                return True
            else:
                logger.error(f"Erro ao reiniciar conexão: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao reiniciar conexão: {str(e)}")
            return False
    
    @retry(max_attempts=3, delay=1.0)
    @log_api_call("zapi_connection_status")
    def is_connected(self) -> bool:
        """Verifica se está conectado ao WhatsApp"""
        url = f"{self.base_url}/status"
        
        try:
            logger.info(f"Verificando status de conexão")
            response = requests.get(url, headers=self.headers)
            
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Resposta: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                connected = result.get("connected", False)
                status = result.get("status", "unknown")
                logger.info(f"Status de conexão: {status} (Conectado: {'Sim' if connected else 'Não'})")
                return connected
            else:
                logger.error(f"Erro ao verificar status: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return False
    
    @retry(max_attempts=3, delay=1.0)
    @log_api_call("zapi_send_message")
    def send_message(self, message: WhatsAppMessage) -> Optional[WhatsAppMessage]:
        """Envia uma mensagem via Z-API"""
        # Valida o número de telefone
        if not PhoneFormatter.is_valid(message.phone):
            logger.error(f"Número de telefone inválido: {message.phone}")
            return None
            
        # Formata o número para a API (com prefixo 55)
        api_phone = PhoneFormatter.format_to_api(message.phone)
        
        # Determina o endpoint com base no tipo de mensagem
        endpoint = "send-text" if message.message_type == MessageType.TEXT else "send-media"
        url = f"{self.base_url}/{endpoint}"
        
        # Prepara o payload
        payload = {
            "phone": api_phone,
            "message": message.message,
            "delayMessage": max(2, len(message.message) // 20),  # Delay baseado no tamanho da mensagem
            "delayTyping": max(3, len(message.message) // 15)    # Tempo digitando proporcional ao tamanho
        }
        
        # Adiciona parâmetros de mídia se necessário
        if message.message_type != MessageType.TEXT:
            payload["url"] = message.media_url
            if message.caption:
                payload["caption"] = message.caption
        
        try:
            logger.info(f"Enviando mensagem para {api_phone}")
            logger.debug(f"Payload: {json.dumps(payload)}")
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Resposta: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                message.message_id = data.get("messageId")
                message.status = "sent"
                logger.info(f"Mensagem enviada com sucesso! ID: {message.message_id}")
                
                # Atualiza o status do contato para ativo
                db_phone = PhoneFormatter.format_to_db(message.phone)
                logger.info(f"Atualizando status do contato {db_phone} para ativo")
                self.contact_service.mark_as_active(db_phone)
                logger.info(f"Status do contato atualizado para ativo")
                
                return message
            else:
                logger.error(f"Erro ao enviar mensagem: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return None