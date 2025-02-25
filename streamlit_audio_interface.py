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

def encode_audio_to_base64(audio_path: str) -> str:
    """Converte um arquivo de áudio para base64"""
    try:
        with open(audio_path, 'rb') as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logger.error(f"Erro ao codificar áudio: {str(e)}")
        return None

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
            'ZAPI_INSTANCE_ID': Config.ZAPI_INSTANCE_ID,
            'ZAPI_TOKEN': Config.ZAPI_TOKEN,
            'ZAPI_SECURITY_TOKEN': Config.ZAPI_SECURITY_TOKEN,
            'ZAPI_SENDER_NUMBER': Config.ZAPI_SENDER_NUMBER,
            'DEFAULT_CLIENT_NUMBER': Config.DEFAULT_CLIENT_NUMBER,
            'TEST_NUMBER_PRIMARY': Config.TEST_NUMBERS.get('primary', ''),
            'TEST_NUMBER_SECONDARY': Config.TEST_NUMBERS.get('secondary', '')
        }

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
    
    # Expander para configurações da API
    with st.expander("Configuração da API Z-API"):
        st.caption("Configure suas credenciais da Z-API")
        
        # Campos de configuração
        instance_id = st.text_input("Instance ID", value=st.session_state.config.get('ZAPI_INSTANCE_ID', ''), key="config_instance_id")
        token = st.text_input("Token", value=st.session_state.config.get('ZAPI_TOKEN', ''), key="config_token")
        security_token = st.text_input("Security Token", value=st.session_state.config.get('ZAPI_SECURITY_TOKEN', ''), type="password", key="config_security_token")
        sender_number = st.text_input("Número do Remetente", value=st.session_state.config.get('ZAPI_SENDER_NUMBER', ''), key="config_sender")
        
        # Botão para salvar configuração
        if st.button("💾 Salvar Configuração"):
            # Atualiza a sessão
            config_data = {
                'ZAPI_INSTANCE_ID': instance_id,
                'ZAPI_TOKEN': token,
                'ZAPI_SECURITY_TOKEN': security_token,
                'ZAPI_SENDER_NUMBER': sender_number
            }
            
            # Atualiza a sessão e o objeto Config
            st.session_state.config.update(config_data)
            Config.update_config(config_data)
            
            # Salva no arquivo .env
            if save_env_file(st.session_state.config):
                st.success("✅ Configuração salva com sucesso!")
            else:
                st.error("❌ Erro ao salvar configuração!")

# Título e descrição principal
st.title("🎵 Envio de Áudio via WhatsApp")
st.subheader("Envie áudios para qualquer número do WhatsApp usando a Z-API")

# Tabs para diferentes funcionalidades
tab1, tab2 = st.tabs(["📱 Envio Individual", "📢 Envio em Massa"])

with tab1:
    # Layout em colunas para envio individual
    col1, col2 = st.columns([3, 2])

    with col1:
        # Upload de arquivo de áudio
        st.subheader("Carregar arquivo de áudio")
        uploaded_file = st.file_uploader("Selecione um arquivo de áudio", type=["mp3", "wav", "ogg"], key="upload_individual")
        
        # Separador
        st.divider()
        
        # Entrada para o número de telefone
        phone_number = st.text_input(
            "Número do WhatsApp (ex: 5521999999999)",
            placeholder="Digite o número com DDI e DDD",
            key="phone_individual"
        )
        
        # Botão de envio
        if st.button("📤 Enviar Áudio", type="primary", key="send_individual"):
            if uploaded_file:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando áudio..."):
                    # Salvar o arquivo temporariamente
                    temp_file_path = save_uploaded_file(uploaded_file)
                    if temp_file_path:
                        # Enviar o áudio
                        result = send_audio(temp_file_path, phone_number)
                        
                        # Mostrar o resultado em um estado de sessão para persistir entre recarregamentos
                        st.session_state.result_individual = result
                    else:
                        st.session_state.result_individual = {"status": "error", "message": "Erro ao processar o arquivo de áudio."}
            else:
                st.session_state.result_individual = {"status": "error", "message": "Por favor, selecione um arquivo de áudio."}

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
            if mass_uploaded_file and mass_phone_numbers:
                # Mostrar spinner durante o processamento
                with st.spinner("Enviando áudios para múltiplos destinatários..."):
                    # Salvar o arquivo temporariamente
                    temp_file_path = save_uploaded_file(mass_uploaded_file)
                    if temp_file_path:
                        # Enviar o áudio para múltiplos números
                        result = send_audio(temp_file_path, mass_phone_numbers)
                        
                        # Mostrar o resultado em um estado de sessão para persistir entre recarregamentos
                        st.session_state.result_mass = result
                    else:
                        st.session_state.result_mass = {"status": "error", "message": "Erro ao processar o arquivo de áudio."}
            else:
                if not mass_uploaded_file:
                    st.session_state.result_mass = {"status": "error", "message": "Por favor, selecione um arquivo de áudio."}
                else:
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
    **Formatos suportados:**
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