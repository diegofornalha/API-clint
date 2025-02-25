import streamlit as st
import os
import base64
import requests
import tempfile
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
# Importando gTTS para conversão de texto para áudio
# from gtts import gTTS  # Comentado temporariamente devido a problemas de dependência

# Configuração de logging simples
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("streamlit_interface")

# Carrega variáveis do arquivo .env
env_path = Path('.') / '.env'
load_dotenv(env_path)

class Config:
    """Configurações da aplicação"""
    
    # Clint API
    CLINT_API_TOKEN: str = os.getenv('CLINT_API_TOKEN', '')
    
    # Z-API
    ZAPI_INSTANCE_ID: str = os.getenv('ZAPI_INSTANCE_ID', '')
    ZAPI_TOKEN: str = os.getenv('ZAPI_TOKEN', '')
    ZAPI_SECURITY_TOKEN: str = os.getenv('ZAPI_SECURITY_TOKEN', '')
    
    # WhatsApp Numbers
    ZAPI_SENDER_NUMBER: str = os.getenv('ZAPI_SENDER_NUMBER', '')
    DEFAULT_CLIENT_NUMBER: str = os.getenv('DEFAULT_CLIENT_NUMBER', '')
    TEST_NUMBERS: dict = {
        'primary': os.getenv('TEST_NUMBER_PRIMARY', ''),
        'secondary': os.getenv('TEST_NUMBER_SECONDARY', '')
    }
    
    # Webhook settings
    WEBHOOK_BASE_URL: str = os.getenv('WEBHOOK_BASE_URL', '')
    WEBHOOK_PORT: int = int(os.getenv('WEBHOOK_PORT', '8000'))
    
    # Ngrok
    NGROK_AUTHTOKEN: str = os.getenv('NGROK_AUTHTOKEN', '')
    
    # URLs de mídia para testes
    MEDIA_URLS = {
        'audio': os.getenv('TEST_AUDIO_URL', 'https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_100KB_MP3.mp3'),
        'video': os.getenv('TEST_VIDEO_URL', 'https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4'),
        'image': os.getenv('TEST_IMAGE_URL', 'https://www.learningcontainer.com/wp-content/uploads/2020/07/Sample-JPEG-Image-File-Download-scaled.jpg'),
        'document': os.getenv('TEST_DOCUMENT_URL', 'https://www.learningcontainer.com/wp-content/uploads/2019/09/sample-pdf-file.pdf')
    }
    
    # Caminhos de arquivos
    AUDIO_TEST_PATH: str = os.getenv('AUDIO_TEST_PATH', '')
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """
        Valida se todas as configurações necessárias estão presentes
        
        Returns:
            Mensagem de erro se alguma configuração estiver faltando, None caso contrário
        """
        missing = []
        
        if not cls.ZAPI_INSTANCE_ID:
            missing.append("ZAPI_INSTANCE_ID")
        
        if not cls.ZAPI_TOKEN:
            missing.append("ZAPI_TOKEN")
        
        if not cls.ZAPI_SECURITY_TOKEN:
            missing.append("ZAPI_SECURITY_TOKEN")
        
        if missing:
            return f"Configurações ausentes: {', '.join(missing)}"
        
        return None
    
    @classmethod
    def get_zapi_base_url(cls) -> str:
        """Retorna a URL base do Z-API"""
        return f"https://api.z-api.io/instances/{cls.ZAPI_INSTANCE_ID}/token/{cls.ZAPI_TOKEN}"
    
    @classmethod
    def update_config(cls, config_dict: Dict[str, str]) -> None:
        """Atualiza as configurações com base em um dicionário"""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
                os.environ[key] = value
            elif key.startswith('TEST_') and key.endswith('_URL'):
                # Atualiza URLs de mídia
                media_key = key.replace('TEST_', '').replace('_URL', '').lower()
                cls.MEDIA_URLS[media_key] = value
                os.environ[key] = value

def encode_audio_to_base64(audio_path: str) -> str:
    """Converte um arquivo de áudio para base64"""
    try:
        with open(audio_path, 'rb') as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logger.error(f"Erro ao codificar áudio: {str(e)}")
        return None

def text_to_audio(text: str, lang: str = 'pt') -> Optional[str]:
    """
    Converte texto para arquivo de áudio usando gTTS
    
    Args:
        text: Texto a ser convertido
        lang: Idioma do texto (padrão: português)
        
    Returns:
        Caminho do arquivo de áudio temporário ou None se falhar
    """
    # Versão temporária - apenas avisa que a funcionalidade está desativada
    logger.warning("Funcionalidade de conversão de texto para áudio temporariamente desativada")
    return None
    
    # Código original comentado:
    """
    try:
        # Cria diretório temporário
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "audio_from_text.mp3")
        
        # Converte texto para áudio
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file)
        
        logger.info(f"Áudio gerado com sucesso: {temp_file}")
        return temp_file
    except Exception as e:
        logger.error(f"Erro ao converter texto para áudio: {str(e)}")
        return None
    """

def send_text(text, phone_numbers):
    """
    Função que processa o envio de texto simples via Z-API
    
    Args:
        text: Texto a ser enviado
        phone_numbers: Número(s) de telefone para envio (string ou lista)
    
    Returns:
        Dict com resultados do envio
    """
    results = {}
    
    # Normaliza para lista de telefones
    if isinstance(phone_numbers, str):
        # Divide a string por vírgulas e remove espaços
        phone_list = [p.strip() for p in phone_numbers.split(',')]
    else:
        phone_list = phone_numbers
    
    # Filtra números vazios
    phone_list = [p for p in phone_list if p]
    
    if not text or not phone_list:
        return {"status": "error", "message": "Por favor, forneça um texto e pelo menos um número de telefone."}
    
    try:
        # Verifica se a configuração é válida
        error = Config.validate()
        if error:
            return {"status": "error", "message": f"Erro de configuração: {error}"}
        
        # URL base da API
        base_url = Config.get_zapi_base_url()
        
        # Headers da requisição
        headers = {
            "Client-Token": Config.ZAPI_SECURITY_TOKEN,
            "Content-Type": "application/json"
        }
        
        # Para cada número na lista
        for phone in phone_list:
            # Remove caracteres não numéricos do telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            if not clean_phone:
                results[phone] = {"status": "error", "message": "Número de telefone inválido"}
                continue
            
            # Payload da requisição
            payload = {
                "phone": clean_phone,
                "message": text
            }
            
            # Envia o texto
            logger.info(f"Enviando texto para {clean_phone}...")
            response = requests.post(
                f"{base_url}/send-text",
                headers=headers,
                json=payload
            )
            
            # Verifica a resposta
            if response.status_code == 200:
                result = response.json()
                results[phone] = {
                    "status": "success",
                    "zaapId": result.get('zaapId', ''),
                    "messageId": result.get('messageId', '')
                }
            else:
                results[phone] = {
                    "status": "error",
                    "message": f"Erro ao enviar texto: {response.text}"
                }
                
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return {"status": "error", "message": f"Erro: {str(e)}"}
    
    # Retorna resultados completos
    return {
        "status": "complete",
        "results": results,
        "summary": {
            "total": len(phone_list),
            "success": sum(1 for r in results.values() if r.get("status") == "success"),
            "failed": sum(1 for r in results.values() if r.get("status") == "error")
        }
    }

def send_audio(audio_file, phone_numbers):
    """
    Função que processa o envio do áudio via Z-API
    
    Args:
        audio_file: Caminho para o arquivo de áudio
        phone_numbers: Número(s) de telefone para envio (string ou lista)
    
    Returns:
        Dict com resultados do envio
    """
    results = {}
    
    # Normaliza para lista de telefones
    if isinstance(phone_numbers, str):
        # Divide a string por vírgulas e remove espaços
        phone_list = [p.strip() for p in phone_numbers.split(',')]
    else:
        phone_list = phone_numbers
    
    # Filtra números vazios
    phone_list = [p for p in phone_list if p]
    
    if not audio_file or not phone_list:
        return {"status": "error", "message": "Por favor, forneça um arquivo de áudio e pelo menos um número de telefone."}
    
    try:
        # Verifica se a configuração é válida
        error = Config.validate()
        if error:
            return {"status": "error", "message": f"Erro de configuração: {error}"}
        
        # URL base da API
        base_url = Config.get_zapi_base_url()
            
        # Converte o áudio para base64
        base64_audio = encode_audio_to_base64(audio_file)
        if not base64_audio:
            return {"status": "error", "message": "Falha ao converter áudio para base64"}
        
        # Headers da requisição
        headers = {
            "Client-Token": Config.ZAPI_SECURITY_TOKEN,
            "Content-Type": "application/json"
        }
        
        # Para cada número na lista
        for phone in phone_list:
            # Remove caracteres não numéricos do telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            if not clean_phone:
                results[phone] = {"status": "error", "message": "Número de telefone inválido"}
                continue
            
            # Payload da requisição
            payload = {
                "phone": clean_phone,
                "audio": base64_audio,
                "waveform": True
            }
            
            # Envia o áudio
            logger.info(f"Enviando áudio para {clean_phone}...")
            response = requests.post(
                f"{base_url}/send-audio",
                headers=headers,
                json=payload
            )
            
            # Verifica a resposta
            if response.status_code == 200:
                result = response.json()
                results[phone] = {
                    "status": "success",
                    "zaapId": result.get('zaapId', ''),
                    "messageId": result.get('messageId', '')
                }
            else:
                results[phone] = {
                    "status": "error",
                    "message": f"Erro ao enviar áudio: {response.text}"
                }
                
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return {"status": "error", "message": f"Erro: {str(e)}"}
    
    # Retorna resultados completos
    return {
        "status": "complete",
        "results": results,
        "summary": {
            "total": len(phone_list),
            "success": sum(1 for r in results.values() if r.get("status") == "success"),
            "failed": sum(1 for r in results.values() if r.get("status") == "error")
        }
    }

def save_uploaded_file(uploaded_file):
    """Salva o arquivo carregado em um arquivo temporário"""
    try:
        # Cria um arquivo temporário
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Salva o arquivo
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return temp_path
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo temporário: {str(e)}")
        return None

def save_env_file(config_data):
    """Salva os dados de configuração em um arquivo .env"""
    try:
        with open('.env', 'w') as f:
            for key, value in config_data.items():
                if value:  # Só escreve se tiver valor
                    f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo .env: {str(e)}")
        return False

def load_env_to_session():
    """Carrega as variáveis de ambiente para a sessão do Streamlit"""
    if not hasattr(st.session_state, 'config'):
        st.session_state.config = {
            # Z-API
            'ZAPI_INSTANCE_ID': Config.ZAPI_INSTANCE_ID,
            'ZAPI_TOKEN': Config.ZAPI_TOKEN,
            'ZAPI_SECURITY_TOKEN': Config.ZAPI_SECURITY_TOKEN,
            
            # WhatsApp Numbers
            'ZAPI_SENDER_NUMBER': Config.ZAPI_SENDER_NUMBER,
            'DEFAULT_CLIENT_NUMBER': Config.DEFAULT_CLIENT_NUMBER,
            'TEST_NUMBER_PRIMARY': Config.TEST_NUMBERS.get('primary', ''),
            'TEST_NUMBER_SECONDARY': Config.TEST_NUMBERS.get('secondary', ''),
            
            # Clint API
            'CLINT_API_TOKEN': Config.CLINT_API_TOKEN,
            
            # Webhook
            'WEBHOOK_BASE_URL': Config.WEBHOOK_BASE_URL,
            'WEBHOOK_PORT': str(Config.WEBHOOK_PORT),
            
            # Ngrok
            'NGROK_AUTHTOKEN': Config.NGROK_AUTHTOKEN,
            
            # Caminhos
            'AUDIO_TEST_PATH': Config.AUDIO_TEST_PATH,
            
            # Mídia
            'TEST_AUDIO_URL': Config.MEDIA_URLS.get('audio', ''),
            'TEST_VIDEO_URL': Config.MEDIA_URLS.get('video', ''),
            'TEST_IMAGE_URL': Config.MEDIA_URLS.get('image', ''),
            'TEST_DOCUMENT_URL': Config.MEDIA_URLS.get('document', '')
        }

def test_api_connection():
    """Testa a conexão com a API Z-API"""
    try:
        error = Config.validate()
        if error:
            return {"status": "error", "message": error}
        
        # URL para testar conexão
        url = f"{Config.get_zapi_base_url()}/connection"
        
        # Headers
        headers = {
            "Client-Token": Config.ZAPI_SECURITY_TOKEN,
            "Content-Type": "application/json"
        }
        
        # Faz a requisição
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("connected"):
                return {"status": "success", "message": "Conectado ao WhatsApp"}
            else:
                return {"status": "warning", "message": "Z-API conectado, mas desconectado do WhatsApp"}
        else:
            return {"status": "error", "message": f"Erro ao verificar conexão: {response.text}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Erro ao testar conexão: {str(e)}"}

# Configuração da página
st.set_page_config(
    page_title="Envio de Áudio via Z-API",
    page_icon="🎵",
    layout="wide"
)

# Carrega as variáveis de ambiente para a sessão
load_env_to_session()

# Barra lateral para configurações
with st.sidebar:
    st.title("⚙️ Configurações")
    
    # Expander para configurações essenciais da Z-API
    with st.expander("Configuração da API Z-API", expanded=True):
        st.caption("Configure suas credenciais da Z-API (obrigatório)")
        
        # Campos de configuração essenciais
        instance_id = st.text_input(
            "Instance ID *", 
            value=st.session_state.config.get('ZAPI_INSTANCE_ID', ''),
            help="ID da instância na Z-API",
            key="config_instance_id"
        )
        
        token = st.text_input(
            "Token *", 
            value=st.session_state.config.get('ZAPI_TOKEN', ''),
            help="Token da API Z-API",
            key="config_token"
        )
        
        security_token = st.text_input(
            "Security Token *", 
            value=st.session_state.config.get('ZAPI_SECURITY_TOKEN', ''),
            type="password",
            help="Token de segurança da Z-API",
            key="config_security_token"
        )
        
        st.markdown("**\* Campos obrigatórios**")
    
    # Expander para números de telefone
    with st.expander("Números de WhatsApp"):
        st.caption("Configure os números de telefone para envio e testes")
        
        sender_number = st.text_input(
            "Número do Remetente", 
            value=st.session_state.config.get('ZAPI_SENDER_NUMBER', ''),
            help="Número que envia as mensagens (ex: 5521999999999)",
            key="config_sender"
        )
        
        default_client = st.text_input(
            "Número do Cliente Padrão", 
            value=st.session_state.config.get('DEFAULT_CLIENT_NUMBER', ''),
            help="Número padrão do cliente (ex: 5521999999999)",
            key="config_default_client"
        )
        
        test_primary = st.text_input(
            "Número de Teste Principal", 
            value=st.session_state.config.get('TEST_NUMBER_PRIMARY', ''),
            help="Número para testes (ex: 5521999999999)",
            key="config_test_primary"
        )
        
        test_secondary = st.text_input(
            "Número de Teste Secundário", 
            value=st.session_state.config.get('TEST_NUMBER_SECONDARY', ''),
            help="Número alternativo para testes",
            key="config_test_secondary"
        )
    
    # Expander para configuração da Clint API
    with st.expander("Configuração da Clint API"):
        st.caption("Configure as credenciais da Clint API")
        
        clint_token = st.text_input(
            "Token da Clint API", 
            value=st.session_state.config.get('CLINT_API_TOKEN', ''),
            help="Token de acesso à API Clint",
            key="config_clint_token"
        )
    
    # Expander para configurações avançadas
    with st.expander("Configurações Avançadas"):
        st.caption("Configurações para webhook e túnel")
        
        webhook_url = st.text_input(
            "URL Base do Webhook", 
            value=st.session_state.config.get('WEBHOOK_BASE_URL', ''),
            help="URL base para webhooks (sem barra no final)",
            key="config_webhook_url"
        )
        
        webhook_port = st.text_input(
            "Porta do Webhook", 
            value=st.session_state.config.get('WEBHOOK_PORT', '8000'),
            help="Porta para o servidor webhook",
            key="config_webhook_port"
        )
        
        ngrok_token = st.text_input(
            "Ngrok AuthToken", 
            value=st.session_state.config.get('NGROK_AUTHTOKEN', ''),
            help="Token de autenticação do Ngrok para exposição de webhooks",
            key="config_ngrok_token"
        )
    
    # Expander para URLs de mídia para testes
    with st.expander("URLs de Mídia para Testes"):
        st.caption("URLs para arquivos de mídia usados em testes")
        
        audio_url = st.text_input(
            "URL de Áudio", 
            value=st.session_state.config.get('TEST_AUDIO_URL', ''),
            help="URL para arquivo de áudio de teste",
            key="config_audio_url"
        )
        
        video_url = st.text_input(
            "URL de Vídeo", 
            value=st.session_state.config.get('TEST_VIDEO_URL', ''),
            help="URL para arquivo de vídeo de teste",
            key="config_video_url"
        )
        
        image_url = st.text_input(
            "URL de Imagem", 
            value=st.session_state.config.get('TEST_IMAGE_URL', ''),
            help="URL para arquivo de imagem de teste",
            key="config_image_url"
        )
        
        document_url = st.text_input(
            "URL de Documento", 
            value=st.session_state.config.get('TEST_DOCUMENT_URL', ''),
            help="URL para arquivo de documento de teste",
            key="config_document_url"
        )
        
        audio_path = st.text_input(
            "Caminho de Áudio Local", 
            value=st.session_state.config.get('AUDIO_TEST_PATH', ''),
            help="Caminho completo para um arquivo de áudio local para testes",
            key="config_audio_path"
        )
    
    # Botão para salvar configuração
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar Configuração", type="primary"):
            # Atualiza a sessão
            config_data = {
                # Z-API
                'ZAPI_INSTANCE_ID': instance_id,
                'ZAPI_TOKEN': token,
                'ZAPI_SECURITY_TOKEN': security_token,
                
                # WhatsApp Numbers
                'ZAPI_SENDER_NUMBER': sender_number,
                'DEFAULT_CLIENT_NUMBER': default_client,
                'TEST_NUMBER_PRIMARY': test_primary,
                'TEST_NUMBER_SECONDARY': test_secondary,
                
                # Clint API
                'CLINT_API_TOKEN': clint_token,
                
                # Webhook
                'WEBHOOK_BASE_URL': webhook_url,
                'WEBHOOK_PORT': webhook_port,
                
                # Ngrok
                'NGROK_AUTHTOKEN': ngrok_token,
                
                # Mídia
                'TEST_AUDIO_URL': audio_url,
                'TEST_VIDEO_URL': video_url,
                'TEST_IMAGE_URL': image_url,
                'TEST_DOCUMENT_URL': document_url,
                'AUDIO_TEST_PATH': audio_path
            }
            
            # Atualiza a sessão e o objeto Config
            st.session_state.config.update(config_data)
            Config.update_config(config_data)
            
            # Salva no arquivo .env
            if save_env_file(st.session_state.config):
                st.success("✅ Configuração salva com sucesso!")
            else:
                st.error("❌ Erro ao salvar configuração!")
    
    with col2:
        if st.button("🔄 Testar Conexão"):
            # Testa a conexão com a API
            result = test_api_connection()
            
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "warning":
                st.warning(result["message"])
            else:
                st.error(result["message"])

# Título e descrição principal
st.title("🎵 Envio de Mensagens via WhatsApp")
st.subheader("Envie áudios ou textos para qualquer número do WhatsApp usando a Z-API")

# Tabs para diferentes funcionalidades
tab1, tab2 = st.tabs(["📱 Envio Individual", "📢 Envio em Massa"])

with tab1:
    # Layout em colunas para envio individual
    col1, col2 = st.columns([3, 2])

    with col1:
        # Upload de arquivo de áudio
        st.subheader("Carregar arquivo de áudio")
        uploaded_file = st.file_uploader("Selecione um arquivo de áudio", type=["mp3", "wav", "ogg"], key="upload_individual")
        
        # OU opção de texto para ser convertido em áudio
        st.subheader("Ou escreva texto para enviar")
        text_input = st.text_area(
            "Digite o texto da mensagem",
            placeholder="Digite seu texto aqui...",
            height=100,
            key="text_individual"
        )
        
        # Checkbox para escolher se converte para áudio ou envia como texto
        if text_input:
            is_convert_to_audio = st.checkbox(
                "Converter texto para mensagem de voz (áudio)",
                value=True,
                help="Se marcado, o texto será convertido para áudio antes de enviar. Se desmarcado, o texto será enviado como mensagem de texto simples.",
                key="convert_individual"
            )
        
        # Separador
        st.divider()
        
        # Entrada para o número de telefone
        phone_number = st.text_input(
            "Número do WhatsApp (ex: 5521999999999)",
            placeholder="Digite o número com DDI e DDD",
            key="phone_individual"
        )
        
        # Botão de envio
        if st.button("📤 Enviar Mensagem", type="primary", key="send_individual"):
            # Verificar se há arquivo ou texto
            temp_file_path = None
            text_to_send = None
            
            if uploaded_file:
                # Se tiver arquivo, usar ele
                with st.spinner("Processando arquivo de áudio..."):
                    temp_file_path = save_uploaded_file(uploaded_file)
            elif text_input:
                # Se tem texto, verifica se é para converter para áudio
                if 'convert_individual' in st.session_state and st.session_state.convert_individual:
                    # Tentativa de converter para áudio
                    with st.spinner("Verificando possibilidade de conversão..."):
                        temp_file_path = text_to_audio(text_input)
                        
                    # Como sabemos que text_to_audio retorna None agora, exibimos o aviso
                    st.warning("⚠️ A conversão de texto para áudio está temporariamente desativada. Enviando como texto simples.")
                    text_to_send = text_input
                else:
                    # Enviar como texto
                    text_to_send = text_input
            else:
                st.session_state.result_individual = {"status": "error", "message": "Por favor, selecione um arquivo de áudio ou digite um texto."}
            
            # Se tem áudio para enviar
            if temp_file_path and phone_number:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando áudio..."):
                    # Enviar o áudio
                    result = send_audio(temp_file_path, phone_number)
                    
                    # Mostrar o resultado em um estado de sessão para persistir entre recarregamentos
                    st.session_state.result_individual = result
            # Se tem texto para enviar
            elif text_to_send and phone_number:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando texto..."):
                    # Enviar o texto
                    result = send_text(text_to_send, phone_number)
                    
                    # Mostrar o resultado em um estado de sessão
                    st.session_state.result_individual = result
            elif (temp_file_path or text_to_send) and not phone_number:
                st.session_state.result_individual = {"status": "error", "message": "Por favor, digite um número de telefone."}

    with col2:
        # Área de resultado
        st.subheader("Status do Envio")
        
        # Verificar e exibir o resultado (se existir)
        if 'result_individual' in st.session_state:
            result = st.session_state.result_individual
            if result.get("status") == "complete":
                st.success("✅ Processamento concluído!")
                
                for phone, phone_result in result.get("results", {}).items():
                    if phone_result.get("status") == "success":
                        st.success(f"✅ Enviado para {phone}: ID {phone_result.get('messageId', '')}")
                    else:
                        st.error(f"❌ Falha para {phone}: {phone_result.get('message', '')}")
                        
            elif "success" in result.get("status", ""):
                st.success(f"✅ Áudio enviado com sucesso!")
                if "results" in result:
                    st.json(result["results"])
            else:
                st.error(result.get("message", "Erro desconhecido no envio"))
        else:
            st.info("O resultado do envio aparecerá aqui.")

with tab2:
    # Layout para envio em massa
    st.subheader("Envio em Massa")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Upload de arquivo de áudio
        st.subheader("Carregar arquivo de áudio")
        mass_uploaded_file = st.file_uploader("Selecione um arquivo de áudio", type=["mp3", "wav", "ogg"], key="upload_mass")
        
        # OU opção de texto para ser convertido em áudio
        st.subheader("Ou escreva texto para enviar")
        mass_text_input = st.text_area(
            "Digite o texto da mensagem",
            placeholder="Digite seu texto aqui...",
            height=100,
            key="text_mass"
        )
        
        # Checkbox para escolher se converte para áudio ou envia como texto
        if mass_text_input:
            is_convert_to_audio_mass = st.checkbox(
                "Converter texto para mensagem de voz (áudio)",
                value=True,
                help="Se marcado, o texto será convertido para áudio antes de enviar. Se desmarcado, o texto será enviado como mensagem de texto simples.",
                key="convert_mass"
            )
        
        # Separador
        st.divider()
        
        # Entrada para múltiplos números de telefone
        mass_phone_numbers = st.text_area(
            "Números de WhatsApp (separados por vírgula)",
            placeholder="Digite os números com DDI e DDD, separados por vírgula\nEx: 5521999999999, 5531888888888",
            height=150,
            key="phones_mass"
        )
        
        # Botão de envio em massa
        if st.button("📤 Enviar para Todos", type="primary", key="send_mass"):
            # Verificar se há arquivo ou texto
            temp_file_path = None
            text_to_send = None
            
            if mass_uploaded_file:
                # Se tiver arquivo, usar ele
                with st.spinner("Processando arquivo de áudio..."):
                    temp_file_path = save_uploaded_file(mass_uploaded_file)
            elif mass_text_input:
                # Se tem texto, verifica se é para converter para áudio
                if 'convert_mass' in st.session_state and st.session_state.convert_mass:
                    # Tentativa de converter para áudio
                    with st.spinner("Verificando possibilidade de conversão..."):
                        temp_file_path = text_to_audio(mass_text_input)
                    
                    # Como sabemos que text_to_audio retorna None agora, exibimos o aviso
                    st.warning("⚠️ A conversão de texto para áudio está temporariamente desativada. Enviando como texto simples.")
                    text_to_send = mass_text_input
                else:
                    # Enviar como texto
                    text_to_send = mass_text_input
            else:
                st.session_state.result_mass = {"status": "error", "message": "Por favor, selecione um arquivo de áudio ou digite um texto."}
            
            # Se tem áudio para enviar
            if temp_file_path and mass_phone_numbers:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando áudios para múltiplos destinatários..."):
                    # Enviar o áudio para múltiplos números
                    result = send_audio(temp_file_path, mass_phone_numbers)
                    
                    # Mostrar o resultado em um estado de sessão
                    st.session_state.result_mass = result
            # Se tem texto para enviar
            elif text_to_send and mass_phone_numbers:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando texto para múltiplos destinatários..."):
                    # Enviar o texto para múltiplos números
                    result = send_text(text_to_send, mass_phone_numbers)
                    
                    # Mostrar o resultado em um estado de sessão
                    st.session_state.result_mass = result
            elif (temp_file_path or text_to_send) and not mass_phone_numbers:
                st.session_state.result_mass = {"status": "error", "message": "Por favor, insira pelo menos um número de telefone."}
    
    with col2:
        # Área de resultado para envio em massa
        st.subheader("Status do Envio em Massa")
        
        # Verificar e exibir o resultado (se existir)
        if 'result_mass' in st.session_state:
            result = st.session_state.result_mass
            
            if result.get("status") == "complete":
                summary = result.get("summary", {})
                
                # Exibe resumo
                st.success(f"✅ Processamento concluído!")
                st.metric("Total de envios", summary.get("total", 0))
                col_success, col_fail = st.columns(2)
                with col_success:
                    st.metric("Enviados com sucesso", summary.get("success", 0))
                with col_fail:
                    st.metric("Falhas", summary.get("failed", 0))
                
                # Detalhes por número
                with st.expander("Ver detalhes por número"):
                    for phone, phone_result in result.get("results", {}).items():
                        if phone_result.get("status") == "success":
                            st.success(f"✅ Enviado para {phone}: ID {phone_result.get('messageId', '')}")
                        else:
                            st.error(f"❌ Falha para {phone}: {phone_result.get('message', '')}")
            else:
                st.error(result.get("message", "Erro desconhecido no envio em massa"))
        else:
            st.info("O resultado do envio aparecerá aqui.")

# Rodapé compartilhado
st.divider()

# Informações adicionais
with st.expander("ℹ️ Informações"):
    st.markdown("""
    **Opções de entrada:**
    - **Arquivo de áudio**: Upload direto de arquivos MP3, WAV, OGG
    - **Texto para áudio**: Digite texto que será convertido em mensagem de voz
    
    **Formatos suportados (para upload de áudio):**
    - MP3
    - WAV
    - OGG
    
    **Requisitos:**
    - Tamanho máximo: 16MB
    - O número deve incluir o código do país (ex: 55 para Brasil)
    - Para envios em massa, separe os números por vírgula
    """)

st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.caption("API Clint - Integração com Z-API") 