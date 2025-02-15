import gradio as gr
import os
import base64
import requests
from clint_api.utils.logger import APILogger

# Configura o logger
logger = APILogger("gradio_audio_interface")

# Configurações da Z-API
INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
TOKEN = "378F94E0EAC7F1CDFFB85BC4"
SECURITY_TOKEN = "F0a93697fc543427aae97a54d8f03ed99S"
BASE_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}"

def encode_audio_to_base64(audio_path: str) -> str:
    """Converte um arquivo de áudio para base64"""
    try:
        with open(audio_path, 'rb') as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            return f"data:audio/mp3;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"❌ Erro ao codificar áudio: {str(e)}")
        return None

def send_audio(audio_file, phone_number):
    """Função que processa o envio do áudio via Z-API"""
    try:
        if not audio_file or not phone_number:
            return "❌ Por favor, forneça um arquivo de áudio e um número de telefone."
            
        # O audio_file pode ser uma tupla (path, None) para upload ou (path, sampling_rate) para gravação
        if isinstance(audio_file, tuple):
            audio_path = audio_file[0]
        else:
            audio_path = audio_file
            
        # Converte o áudio para base64
        base64_audio = encode_audio_to_base64(audio_path)
        if not base64_audio:
            return "❌ Falha ao converter áudio para base64"
        
        # Headers da requisição
        headers = {
            "Client-Token": SECURITY_TOKEN,
            "Content-Type": "application/json"
        }
        
        # Remove caracteres não numéricos do telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Payload da requisição
        payload = {
            "phone": phone_number,
            "audio": base64_audio,
            "waveform": True
        }
        
        # Envia o áudio
        response = requests.post(
            f"{BASE_URL}/send-audio",
            headers=headers,
            json=payload
        )
        
        # Verifica a resposta
        if response.status_code == 200:
            result = response.json()
            return f"""✅ Áudio enviado com sucesso!
            zaapId: {result.get('zaapId')}
            messageId: {result.get('messageId')}"""
        else:
            return f"❌ Erro ao enviar áudio: {response.text}"
            
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# Cria a interface Gradio
with gr.Blocks(title="Envio de Áudio via Z-API") as demo:
    gr.Markdown("# 🎵 Envio de Áudio via WhatsApp")
    gr.Markdown("### Envie áudios para qualquer número do WhatsApp usando a Z-API")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="Selecione ou Grave um Áudio",
                type="filepath",
                sources=["microphone", "upload"]
            )
            phone_input = gr.Textbox(
                label="Número do WhatsApp (ex: 5521999999999)",
                placeholder="Digite o número com DDD e DDI"
            )
            send_btn = gr.Button("📤 Enviar Áudio", variant="primary")
        
        with gr.Column():
            output = gr.Textbox(
                label="Status do Envio",
                placeholder="O resultado aparecerá aqui...",
                lines=4
            )
    
    send_btn.click(
        fn=send_audio,
        inputs=[audio_input, phone_input],
        outputs=output
    )

# Inicia o servidor Gradio com URL pública
demo.launch(share=True) 