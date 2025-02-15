from clint_api.clients.zapi_client import ZAPIClient
from clint_api.utils.logger import APILogger
import requests
import json
from typing import Dict, Any, Optional

# Configura o logger
logger = APILogger("configure_webhooks")

def configure_webhooks(
    instance_id: str,
    token: str,
    security_token: str,
    base_url: str
) -> Dict[str, Any]:
    """
    Configura os webhooks na Z-API
    
    Args:
        instance_id: ID da instância
        token: Token da API
        security_token: Token de segurança
        base_url: URL base para os webhooks (ex: https://seu-dominio.com)
    
    Returns:
        Dict com o status da configuração de cada webhook
    """
    # URLs dos webhooks
    webhook_urls = {
        "on-send": f"{base_url}/webhook-test/zapi",
        "on-disconnect": f"{base_url}/webhook-test/zapi",
        "on-receive": f"{base_url}/webhook-test/zapi",
        "chat-presence": f"{base_url}/webhook-test/zapi",
        "message-status": f"{base_url}/webhook-test/zapi",
        "on-connect": f"{base_url}/webhook-test/zapi"
    }
    
    # URL base da API
    api_base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    
    # Headers comuns
    headers = {
        "Content-Type": "application/json",
        "Client-Token": security_token
    }
    
    # Resultado da configuração
    results = {}
    
    # Configura cada webhook
    for webhook_type, url in webhook_urls.items():
        try:
            # Endpoint específico para cada tipo de webhook
            if webhook_type == "on-receive":
                endpoint = f"{api_base_url}/webhooks/update-webhook-received-delivery"  # Endpoint que inclui mensagens enviadas
            else:
                endpoint = f"{api_base_url}/webhooks/{webhook_type}"
            
            # Payload com a URL do webhook
            payload = {
                "value": url,
                "enabled": True
            }
            
            # Faz a requisição
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload
            )
            
            # Registra o resultado
            results[webhook_type] = {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
            
            # Log do resultado
            if response.status_code == 200:
                logger.info(f"\n✅ Webhook {webhook_type} configurado com sucesso")
                logger.info(f"URL: {url}")
            else:
                logger.error(f"\n❌ Erro ao configurar webhook {webhook_type}")
                logger.error(f"Status: {response.status_code}")
                logger.error(f"Resposta: {response.text}")
            
        except Exception as e:
            results[webhook_type] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"\n❌ Erro ao configurar webhook {webhook_type}: {str(e)}")
    
    return results

def get_current_webhooks(
    instance_id: str,
    token: str,
    security_token: str
) -> Optional[Dict[str, Any]]:
    """
    Obtém a configuração atual dos webhooks
    
    Args:
        instance_id: ID da instância
        token: Token da API
        security_token: Token de segurança
    
    Returns:
        Dict com a configuração atual dos webhooks ou None se houver erro
    """
    try:
        # URL base da API
        api_base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/webhooks"
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Client-Token": security_token
        }
        
        # Faz a requisição
        response = requests.get(
            api_base_url,
            headers=headers
        )
        
        if response.status_code == 200:
            webhooks = response.json()
            logger.info("\n📋 Webhooks atualmente configurados:")
            logger.info(json.dumps(webhooks, indent=2))
            return webhooks
        else:
            logger.error(f"\n❌ Erro ao obter webhooks: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"\n❌ Erro ao obter webhooks: {str(e)}")
        return None

def main():
    """Função principal"""
    # Configurações da Z-API
    instance_id = "3DCC625CC314A038C87896155CBF9532"
    token = "378F94E0EAC7F1CDFFB85BC4"
    security_token = "F0a93697fc543427aae97a54d8f03ed99S"
    
    # URL base para os webhooks (substitua pelo seu domínio)
    base_url = "https://seu-dominio.com"
    
    # Obtém webhooks atuais
    logger.info("\n🔍 Verificando webhooks atuais...")
    current_webhooks = get_current_webhooks(instance_id, token, security_token)
    
    # Configura novos webhooks
    logger.info("\n⚙️ Configurando webhooks...")
    results = configure_webhooks(
        instance_id=instance_id,
        token=token,
        security_token=security_token,
        base_url=base_url
    )
    
    # Log do resultado final
    logger.info("\n📊 Resultado da configuração:")
    logger.info(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 