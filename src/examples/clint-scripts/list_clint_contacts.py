import os
import sys
import requests
from dotenv import load_dotenv
from clint_api.utils.logger import APILogger

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = APILogger("list_clint_contacts")
load_dotenv()

def list_contacts(
    limit: int = 200,
    offset: int = 0,
    page: int = 1,
    origin_id: str = None,
    name: str = None,
    ddi: str = None,
    phone: str = None,
    email: str = None,
    tag_ids: str = None,
    tag_names: str = None
):
    """
    Lista contatos da API Clint com filtros
    
    Args:
        limit: Número máximo de resultados (1-1000)
        offset: Número de registros para pular
        page: Página dos resultados
        origin_id: Filtrar por ID de origem
        name: Filtrar por nome do contato
        ddi: Filtrar por DDI
        phone: Filtrar por telefone
        email: Filtrar por email
        tag_ids: Filtrar por IDs de tags (separados por vírgula)
        tag_names: Filtrar por nomes de tags (separados por vírgula)
    """
    # Configuração da API
    api_token = os.getenv("CLINT_API_TOKEN")
    base_url = "https://api.clint.digital/v1"
    
    # Headers
    headers = {
        "api-token": api_token,
        "accept": "application/json"
    }
    
    # Parâmetros
    params = {
        "limit": min(max(1, limit), 1000),  # Garante que está entre 1 e 1000
        "offset": max(0, offset),  # Garante que não é negativo
        "page": max(1, page)  # Garante que não é menor que 1
    }
    
    # Adiciona filtros opcionais
    if origin_id:
        params["origin_id"] = origin_id
    if name:
        params["name"] = name
    if ddi:
        params["ddi"] = ddi
    if phone:
        params["phone"] = phone
    if email:
        params["email"] = email
    if tag_ids:
        params["tag_ids"] = tag_ids
    if tag_names:
        params["tag_names"] = tag_names
    
    try:
        # Faz a requisição
        logger.info(f"\nListando contatos da API Clint")
        logger.info(f"URL: {base_url}/contacts")
        logger.info(f"Parâmetros: {params}")
        
        response = requests.get(
            f"{base_url}/contacts",
            headers=headers,
            params=params
        )
        
        # Log da resposta
        logger.info(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verifica se é uma lista ou está dentro de uma chave
            contacts = data if isinstance(data, list) else data.get("data", [])
            
            # Log dos resultados
            logger.info(f"\nTotal de contatos: {len(contacts)}")
            logger.info("\nContatos:")
            
            for contact in contacts:
                logger.info("\n---")
                logger.info(f"ID: {contact.get('id')}")
                logger.info(f"Nome: {contact.get('name')}")
                logger.info(f"Telefone: {contact.get('fullPhone')}")
                logger.info(f"Email: {contact.get('email')}")
                
                # Processa tags
                tags = contact.get("tags", [])
                tag_names = [tag.get("name", "") for tag in tags if isinstance(tag, dict)]
                logger.info(f"Tags: {', '.join(tag_names) if tag_names else 'Nenhuma'}")
                
                # Campos personalizados
                fields = contact.get("fields", {})
                if fields:
                    logger.info("Campos personalizados:")
                    for field_name, field_value in fields.items():
                        logger.info(f"  {field_name}: {field_value}")
            
            return contacts
        else:
            logger.error(f"Erro ao listar contatos: {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Erro ao listar contatos: {str(e)}")
        return []

def main():
    try:
        # Lista todos os contatos (máximo de 200 por página)
        contacts = list_contacts(
            limit=200,  # Número de contatos por página
            page=1,    # Primeira página
            # Adicione filtros conforme necessário:
            # name="João",
            # tag_names="Cliente,VIP",
            # etc...
        )
        
        # Log do total
        logger.info(f"\nTotal de contatos retornados: {len(contacts)}")
        
    except Exception as e:
        logger.error(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main() 