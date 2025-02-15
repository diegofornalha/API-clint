import subprocess
import time
import sys
import json
from clint_api.utils.logger import APILogger
from configure_webhooks import configure_webhooks, get_current_webhooks
import requests

# Configura o logger
logger = APILogger("start_webhook_server")

def start_localtunnel(port: int) -> str:
    """
    Inicia o Localtunnel para expor o servidor local
    
    Args:
        port: Porta do servidor local
        
    Returns:
        URL do tunnel
    """
    logger.info(f"\n🚇 Iniciando Localtunnel na porta {port}...")
    
    # Define um subdomínio fixo para o tunnel
    subdomain = "teste"  # Subdomínio fixo
    max_retries = 3
    current_try = 0
    
    while current_try < max_retries:
        try:
            # Inicia o Localtunnel com subdomínio fixo
            process = subprocess.Popen(
                ['npx', 'localtunnel', '--port', str(port), '--subdomain', subdomain, '--local-host', '201.50.126.167'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Aguarda a URL do tunnel
            for line in process.stdout:
                if "your url is:" in line.lower():
                    tunnel_url = line.split("is:")[-1].strip()
                    logger.info(f"\n✅ Localtunnel iniciado: {tunnel_url}")
                    return tunnel_url
                elif "domain in use" in line.lower():
                    raise Exception("Subdomínio em uso")
            
            raise Exception("Não foi possível obter a URL do Localtunnel")
            
        except Exception as e:
            current_try += 1
            if "Subdomínio em uso" in str(e) and current_try < max_retries:
                # Se o subdomínio estiver em uso, tenta com um número
                subdomain = f"teste-{current_try}"
                logger.info(f"\n⚠️ Subdomínio em uso, tentando: {subdomain}")
                continue
            elif current_try >= max_retries:
                raise Exception(f"Não foi possível iniciar o Localtunnel após {max_retries} tentativas")
            else:
                raise e

def start_webhook_server(port: int) -> subprocess.Popen:
    """
    Inicia o servidor de webhooks
    
    Args:
        port: Porta para o servidor
        
    Returns:
        Processo do servidor
    """
    logger.info(f"\n🚀 Iniciando servidor de webhooks na porta {port}...")
    
    # Inicia o servidor
    process = subprocess.Popen(
        ['python', 'src/examples/z-api-scripts/webhook_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Aguarda o servidor iniciar
    time.sleep(2)
    
    if process.poll() is not None:
        raise Exception("Servidor falhou ao iniciar")
    
    logger.info("\n✅ Servidor iniciado com sucesso!")
    return process

def main():
    """Função principal"""
    # Configurações
    PORT = 8000
    INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
    TOKEN = "378F94E0EAC7F1CDFFB85BC4"
    SECURITY_TOKEN = "F0a93697fc543427aae97a54d8f03ed99S"
    
    try:
        # Inicia o servidor
        server_process = start_webhook_server(PORT)
        
        # Inicia o Localtunnel
        tunnel_url = start_localtunnel(PORT)
        
        # Obtém webhooks atuais
        logger.info("\n🔍 Verificando webhooks atuais...")
        current_webhooks = get_current_webhooks(
            instance_id=INSTANCE_ID,
            token=TOKEN,
            security_token=SECURITY_TOKEN
        )
        
        # Configura os webhooks com a URL do Localtunnel
        logger.info("\n⚙️ Configurando webhooks...")
        
        # Primeiro configura o webhook de recebimento com a opção de notificar mensagens enviadas
        logger.info("\n🔄 Configurando webhook de recebimento com notificação de mensagens enviadas...")
        delivery_endpoint = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/update-webhook-received-delivery"
        delivery_payload = {
            "value": f"{tunnel_url}/webhook-test/zapi",
            "enabled": True
        }
        delivery_response = requests.put(
            delivery_endpoint,
            headers={"Content-Type": "application/json", "Client-Token": SECURITY_TOKEN},
            json=delivery_payload
        )
        logger.info(f"Status da configuração de recebimento: {delivery_response.status_code}")
        
        # Configura os demais webhooks
        results = configure_webhooks(
            instance_id=INSTANCE_ID,
            token=TOKEN,
            security_token=SECURITY_TOKEN,
            base_url=tunnel_url
        )
        
        # Log do resultado
        logger.info("\n📊 Resultado da configuração:")
        logger.info(f"URL base: {tunnel_url}")
        logger.info("\nEndpoints configurados:")
        for webhook_type, result in results.items():
            status = "✅" if result["status"] == "success" else "❌"
            logger.info(f"{status} {webhook_type}: {tunnel_url}/webhook-test/zapi")
        
        # Mantém o servidor rodando
        logger.info("\n👀 Monitorando eventos... (Ctrl+C para parar)")
        server_process.wait()
        
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Encerrando servidor...")
        if 'server_process' in locals():
            server_process.terminate()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Erro: {str(e)}")
        if 'server_process' in locals():
            server_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 