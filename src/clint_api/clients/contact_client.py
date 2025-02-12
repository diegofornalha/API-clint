import requests
import json
from typing import Dict, Any, List, Optional

from ..models.contact import Contato
from ..exceptions.api_exceptions import (
    ClintAPIException,
    ContactNotFoundException,
    ContactAlreadyExistsException,
    APIAuthenticationError
)

class ContactClient:
    """Cliente para gerenciamento de contatos na API Clint"""
    
    def __init__(self, api_token: str, base_url: str = "https://api.clint.digital/v1"):
        self.base_url = base_url
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-token": api_token
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Processa a resposta da API e trata erros"""
        try:
            if response.status_code == 404:
                raise ContactNotFoundException(f"Contato não encontrado. Status: {response.status_code}, Resposta: {response.text}")
            elif response.status_code == 400:
                if "already exists" in response.text.lower():
                    raise ContactAlreadyExistsException(f"Email já cadastrado. Status: {response.status_code}, Resposta: {response.text}")
                raise ClintAPIException(f"Erro na requisição. Status: {response.status_code}, Resposta: {response.text}")
            elif response.status_code == 401:
                raise APIAuthenticationError(f"Token de API inválido. Status: {response.status_code}, Resposta: {response.text}")
            elif response.status_code not in [200, 201, 204]:
                raise ClintAPIException(f"Erro na API. Status: {response.status_code}, Resposta: {response.text}")
            
            return response.json() if response.text else {}
        except ValueError as e:
            raise ClintAPIException(f"Resposta inválida da API: {str(e)}. Status: {response.status_code}, Resposta: {response.text}")
        except Exception as e:
            raise ClintAPIException(f"Erro inesperado: {str(e)}. Status: {response.status_code}, Resposta: {response.text}")

    def create_contact(self, contact: Contato) -> Dict[str, Any]:
        """Cria um novo contato"""
        url = f"{self.base_url}/contacts"
        response = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(contact.to_dict())
        )
        
        result = self._handle_response(response)
        if isinstance(result, dict):
            if "data" in result and isinstance(result["data"], dict):
                contact.id = result["data"].get("id")
            elif "id" in result:
                contact.id = result["id"]
        return result

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Busca um contato pelo ID"""
        url = f"{self.base_url}/contacts/{contact_id}"
        response = requests.get(url, headers=self.headers)
        result = self._handle_response(response)
        return result

    def update_contact(self, contact_id: str, contact: Contato) -> Dict[str, Any]:
        """Atualiza um contato existente"""
        if not contact.id:
            raise ValueError("ID do contato é necessário para atualização")
        
        url = f"{self.base_url}/contacts/{contact.id}"
        response = requests.put(
            url,
            headers=self.headers,
            data=json.dumps(contact.to_dict())
        )
        self._handle_response(response)
        return response.json()

    def delete_contact(self, contact_id: str) -> bool:
        """Remove um contato pelo ID"""
        url = f"{self.base_url}/contacts/{contact_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            self._handle_response(response)
            print(f"Contato {contact_id} deletado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro detalhado ao deletar contato: URL={url}, Headers={self.headers}, Erro={str(e)}")
            raise

    def list_contacts(self, page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Lista contatos com paginação"""
        url = f"{self.base_url}/contacts"
        params = {"page": page, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        result = self._handle_response(response)
        return result.get("data", [])

    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Busca contatos por termo de pesquisa"""
        url = f"{self.base_url}/contacts/search"
        params = {"q": query}
        response = requests.get(url, headers=self.headers, params=params)
        result = self._handle_response(response)
        return result.get("data", []) 