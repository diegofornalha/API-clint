from typing import List, Optional
from ..clients.contact_client import ContactClient
from ..clients.zapi_client import ZAPIClient
from ..models.contact import Contato
from ..models.whatsapp_message import WhatsAppMessage

class IntegrationService:
    """Serviço de integração entre Clint e Z-API"""
    
    def __init__(self, contact_client: ContactClient, zapi_client: ZAPIClient):
        self.contact_client = contact_client
        self.zapi_client = zapi_client
    
    def sync_contacts(self) -> List[Contato]:
        """Sincroniza contatos entre Clint e Z-API"""
        # Obtém contatos do Clint
        clint_contacts = self.contact_client.list_contacts()
        
        # TODO: Implementar sincronização com Z-API
        return []
    
    def send_message(self, contact: Contato, message: WhatsAppMessage) -> bool:
        """Envia mensagem para um contato"""
        try:
            # Envia mensagem via Z-API
            result = self.zapi_client.send_message(message)
            return result.success
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return False

    def send_message_to_contact(
        self,
        contact_id: str,
        message_text: str
    ) -> Optional[WhatsAppMessage]:
        """
        Envia uma mensagem de WhatsApp para um contato do Clint
        
        Args:
            contact_id: ID do contato no Clint
            message_text: Texto da mensagem
            
        Returns:
            WhatsAppMessage com status do envio ou None se falhar
        """
        # Verifica conexão com WhatsApp
        if not self.zapi_client.is_connected():
            raise RuntimeError("Z-API não está conectado ao WhatsApp")
        
        # Busca o contato
        contact = self.contact_client.get_contact(contact_id)
        
        # Prepara o número de telefone (remove caracteres não numéricos)
        phone = f"{contact.ddi}{contact.phone}".replace("+", "")
        
        # Cria e envia a mensagem
        message = WhatsAppMessage(
            phone=phone,
            message=message_text,
            instance_id=self.zapi_client.instance_id,
            token=self.zapi_client.token
        )
        
        return self.zapi_client.send_text_message(message)
    
    def send_bulk_message(
        self,
        message_text: str,
        filter_query: Optional[str] = None
    ) -> List[WhatsAppMessage]:
        """
        Envia uma mensagem em massa para contatos do Clint
        
        Args:
            message_text: Texto da mensagem
            filter_query: Filtro opcional para buscar contatos
            
        Returns:
            Lista de WhatsAppMessage com status dos envios
        """
        # Verifica conexão com WhatsApp
        if not self.zapi_client.is_connected():
            raise RuntimeError("Z-API não está conectado ao WhatsApp")
        
        # Busca contatos
        contacts = []
        if filter_query:
            contacts = self.contact_client.search_contacts(filter_query)
        else:
            contacts = self.contact_client.list_contacts()
        
        # Envia mensagens
        messages = []
        for contact in contacts:
            try:
                message = self.send_message_to_contact(
                    contact.id,
                    message_text
                )
                if message:
                    messages.append(message)
            except Exception as e:
                print(f"Erro ao enviar mensagem para {contact.name}: {str(e)}")
        
        return messages 