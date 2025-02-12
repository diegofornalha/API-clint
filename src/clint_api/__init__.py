from .clients.contact_client import ContactClient
from .clients.zapi_client import ZAPIClient
from .models.contact import Contato, ContatoStatus
from .models.whatsapp_message import WhatsAppMessage
from .services.integration_service import IntegrationService
from .services.contact_service import ContactService
from .exceptions.api_exceptions import (
    ClintAPIException,
    ContactNotFoundException,
    ContactAlreadyExistsException,
    APIAuthenticationError
)

__all__ = [
    'ContactClient',
    'ZAPIClient',
    'WhatsAppMessage',
    'IntegrationService',
    'ClintAPIException',
    'ContactNotFoundException',
    'ContactAlreadyExistsException',
    'APIAuthenticationError'
]

# Versão do pacote
__version__ = "1.0.0" 