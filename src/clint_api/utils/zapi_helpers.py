"""
Funções utilitárias para interação com a Z-API.

Este módulo contém funções comumente usadas na integração com a Z-API,
evitando código duplicado nos scripts de exemplo.
"""

import time
import json
import subprocess
import requests
from typing import Dict, Any, Optional, List, Tuple
import base64
import os
from pathlib import Path

from ..clients.zapi_client import ZAPIClient
from ..utils.logger import APILogger
from ..utils.config import Config

logger = APILogger("zapi_helpers")

def check_connection(client: ZAPIClient, max_retries: int = 3, retry_interval: int = 5) -> bool:
    """
    Verifica se o WhatsApp está conectado, com tentativas de reconexão

    Args:
        client: Instância do ZAPIClient
        max_retries: Número máximo de tentativas
        retry_interval: Intervalo entre tentativas em segundos

    Returns:
        True se conectado, False caso contrário
    """
    for i in range(max_retries):
        if i > 0:
            logger.info(f"\nTentativa {i+1} de {max_retries}...")
            
        if client.is_connected():
            logger.info("\n✅ WhatsApp conectado!")
            return True
        
        if i < max_retries - 1:
            logger.info(f"\nWhatsApp não conectado. Tentando novamente em {retry_interval} segundos...")
            time.sleep(retry_interval)
    
    logger.error("\n❌ WhatsApp não está conectado após várias tentativas!")
    logger.info("\nPara conectar:")
    logger.info("1. Acesse https://app.z-api.io")
    logger.info("2. Localize sua instância")
    logger.info("3. Escaneie o QR Code com o WhatsApp")
    logger.info(f"4. Use o número {Config.ZAPI_SENDER_NUMBER}")
    
    return False

def restart_connection(instance_id: str, token: str, security_token: str) -> bool:
    """
    Reinicia a conexão do WhatsApp

    Args:
        instance_id: ID da instância Z-API
        token: Token da Z-API
        security_token: Token de segurança da Z-API

    Returns:
        True se o comando foi enviado com sucesso, False caso contrário
    """
    try:
        logger.info("\nReiniciando conexão com o WhatsApp...")
        
        # URL para reiniciar a conexão
        url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/restart-connection"
        
        # Headers
        headers = {
            "Client-Token": security_token,
            "Content-Type": "application/json"
        }
        
        # Faz a requisição
        response = requests.post(url, headers=headers)
        
        if response.status_code in [200, 201]:
            logger.info("\n✅ Comando de reinicialização enviado com sucesso!")
            logger.info("\nAguardando 10 segundos para a reinicialização...")
            time.sleep(10)
            
            # Verifica o status após o restart
            status_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/connection"
            status_response = requests.get(status_url, headers=headers)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                logger.info(f"\nStatus após reinicialização: {json.dumps(status_data, indent=2)}")
                return True
            else:
                logger.error(f"\n❌ Erro ao verificar status após reinicialização: {status_response.text}")
                return False
        else:
            logger.error(f"\n❌ Erro ao reiniciar conexão: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")
        return False

def encode_media_to_base64(file_path: str) -> Optional[str]:
    """
    Codifica um arquivo de mídia para base64

    Args:
        file_path: Caminho do arquivo

    Returns:
        String base64 ou None se falhar
    """
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"❌ Erro ao converter arquivo para base64: {str(e)}")
        return None

def start_localtunnel(port: int, retries: int = 3) -> Optional[str]:
    """
    Inicia o Localtunnel para expor a porta local

    Args:
        port: Porta local a ser exposta
        retries: Número de tentativas

    Returns:
        URL do Localtunnel ou None se falhar
    """
    current_try = 0
    max_retries = retries
    subdomain = "clint-webhook-test"
    
    while current_try < max_retries:
        try:
            logger.info(f"\nIniciando Localtunnel na porta {port}...")
            
            if current_try > 0:
                # Se não é a primeira tentativa, usa um subdomínio diferente
                subdomain = f"clint-webhook-{current_try}"
                
            # Executa o comando localtunnel
            cmd = ["lt", "--port", str(port), "--subdomain", subdomain]
            tunnel = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Aguarda e lê a primeira linha
            for line in tunnel.stdout:
                if "your url is:" in line.lower():
                    url = line.split("is:")[-1].strip()
                    logger.info(f"\n✅ Localtunnel iniciado: {url}")
                    return url
            
            # Se chegou aqui, não conseguiu ler a URL
            raise Exception("Não foi possível obter a URL do Localtunnel")
            
        except Exception as e:
            current_try += 1
            if "Subdomínio em uso" in str(e) and current_try < max_retries:
                # Se o subdomínio estiver em uso, tenta com um número
                logger.info(f"\n⚠️ Subdomínio em uso, tentando: {subdomain}")
                continue
            elif current_try >= max_retries:
                logger.error(f"❌ Não foi possível iniciar o Localtunnel após {max_retries} tentativas")
                return None
            else:
                logger.error(f"❌ Erro ao iniciar Localtunnel: {str(e)}")
                return None

def get_current_webhooks(instance_id: str, token: str, security_token: str) -> Dict[str, Any]:
    """
    Obtém os webhooks configurados na Z-API

    Args:
        instance_id: ID da instância Z-API
        token: Token da Z-API
        security_token: Token de segurança da Z-API

    Returns:
        Dicionário com os webhooks atuais
    """
    try:
        # URL para obter os webhooks
        url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/webhooks"
        
        # Headers
        headers = {
            "Client-Token": security_token,
            "Content-Type": "application/json"
        }
        
        # Faz a requisição
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"\nWebhooks atuais:\n{json.dumps(data, indent=2)}")
            return data
        else:
            logger.error(f"\n❌ Erro ao obter webhooks: {response.text}")
            return {}
            
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")
        return {}

def configure_webhooks(
    instance_id: str, 
    token: str, 
    security_token: str, 
    base_url: str
) -> Dict[str, Any]:
    """
    Configura todos os webhooks da Z-API

    Args:
        instance_id: ID da instância Z-API
        token: Token da Z-API
        security_token: Token de segurança da Z-API
        base_url: URL base para os webhooks (sem barra no final)

    Returns:
        Dicionário com os resultados da configuração
    """
    # Lista de webhooks a serem configurados
    webhook_endpoints = {
        "on-message-received": "/webhooks/zapi/on-receive",
        "on-message-sent": "/webhooks/zapi/on-send",
        "on-whatsapp-disconnected": "/webhooks/zapi/on-disconnect",
        "on-whatsapp-connected": "/webhooks/zapi/on-connect",
        "on-chat-presence": "/webhooks/zapi/chat-presence",
        "on-status-message": "/webhooks/zapi/message-status"
    }
    
    results = {}
    
    for webhook_type, endpoint in webhook_endpoints.items():
        try:
            # URL para configurar o webhook
            url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/hook-{webhook_type}"
            
            # Headers
            headers = {
                "Client-Token": security_token,
                "Content-Type": "application/json"
            }
            
            # Payload
            payload = {
                "value": f"{base_url}{endpoint}"
            }
            
            # Faz a requisição
            logger.info(f"\nConfigurando webhook {webhook_type}...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Webhook {webhook_type} configurado com sucesso!")
                results[webhook_type] = {
                    "success": True,
                    "url": payload["value"]
                }
            else:
                logger.error(f"❌ Erro ao configurar webhook {webhook_type}: {response.text}")
                results[webhook_type] = {
                    "success": False,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook {webhook_type}: {str(e)}")
            results[webhook_type] = {
                "success": False,
                "error": str(e)
            }
    
    return results 