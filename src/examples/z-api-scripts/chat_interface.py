import gradio as gr
import json
import time
import signal
import sys
from datetime import datetime
from threading import Thread, Event
from queue import Queue
import requests
from clint_api.utils.logger import APILogger
from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.services.message_history_service import MessageHistoryService
from clint_api.models.message_history import MessageDirection

# Configurações
INSTANCE_ID = "3DCC625CC314A038C87896155CBF9532"
TOKEN = "378F94E0EAC7F1CDFFB85BC4"
SECURITY_TOKEN = "F0a93697fc543427aae97a54d8f03ed99S"

# Inicializa serviços
logger = APILogger("chat_interface")
history_service = MessageHistoryService()

# Controles globais
event_queue = Queue()
stop_event = Event()
poll_thread = None

def signal_handler(signum, frame):
    """Manipulador de sinais para encerramento gracioso"""
    logger.info("\n🛑 Encerrando servidor...")
    stop_event.set()
    sys.exit(0)

# Registra handlers para SIGINT e SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def format_event(event_type: str, data: dict) -> str:
    """Formata um evento para exibição"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {event_type.upper()}\n"
    formatted += json.dumps(data, indent=2)
    formatted += "\n" + "-"*50 + "\n"
    return formatted

def format_chat_message(history_item) -> tuple:
    """Formata uma mensagem do histórico para exibição no chat"""
    timestamp = history_item.timestamp.strftime("%H:%M:%S")
    
    if history_item.direction == MessageDirection.SENT:
        status_emoji = "✅" if history_item.status == "sent" else "⏳"
        content = f"{status_emoji} Você ({timestamp}): {history_item.message}"
        return (content, None)
    else:
        status_emoji = "📱"
        content = f"{status_emoji} Contato ({timestamp}): {history_item.message}"
        return (None, content)

def load_chat_history(phone: str) -> list:
    """Carrega o histórico de mensagens enviadas de um número"""
    if not phone:
        return []
        
    try:
        # Obtém histórico ordenado por data (mais antigas primeiro)
        history = history_service.get_chat_history(phone)
        messages = []
        
        # Formata apenas mensagens enviadas para exibição
        for item in history:
            if item.direction == MessageDirection.SENT:
                timestamp = item.timestamp.strftime("%H:%M:%S")
                status_emoji = "✅" if item.status == "sent" else "⏳"
                content = f"{status_emoji} Enviada ({timestamp}): {item.message}"
                messages.append((content, None))
            
        logger.info(f"Histórico carregado: {len(messages)} mensagens enviadas")
        
        return messages
    except Exception as e:
        logger.error(f"Erro ao carregar histórico: {str(e)}")
        return []

def send_message(phone: str, message: str, chat_history: list) -> tuple[str, list, str]:
    """Envia uma mensagem via Z-API"""
    try:
        if not phone or not message:
            return "❌ Por favor, preencha o número e a mensagem", chat_history, message
        
        client = ZAPIClient(INSTANCE_ID, TOKEN, SECURITY_TOKEN)
        
        if not client.is_connected():
            return "❌ WhatsApp não está conectado! Verifique a conexão.", chat_history, message
        
        whatsapp_message = WhatsAppMessage(
            phone=phone,
            message=message,
            instance_id=INSTANCE_ID,
            token=TOKEN,
            message_type=MessageType.TEXT
        )
        
        result = client.send_message(whatsapp_message)
        
        if result and result.message_id:
            # Registra a mensagem no histórico
            history_service.add_sent_message(result)
            
            # Atualiza o histórico
            new_history = load_chat_history(phone)
            
            # Retorna status, histórico atualizado e limpa o campo de mensagem
            status = f"✅ Mensagem enviada com sucesso!\nID: {result.message_id}\nStatus: {result.status}"
            return status, new_history, ""
        else:
            return "❌ Erro ao enviar mensagem", chat_history, message
            
    except Exception as e:
        return f"❌ Erro: {str(e)}", chat_history, message

def poll_events(phone: str, sent_history: gr.Chatbot, received_history: gr.Chatbot) -> None:
    """Monitora eventos do servidor local"""
    logger.info("🔄 Iniciando monitoramento de eventos...")
    last_update = datetime.now()
    
    while not stop_event.is_set():
        try:
            response = requests.get("http://localhost:8000/events")
            if response.status_code == 200:
                events = response.json()
                current_time = datetime.now()
                
                # Processa eventos recebidos
                for event_type, event_list in events.items():
                    for event in event_list:
                        event_time = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
                        
                        # Só processa eventos novos
                        if event_time > last_update:
                            # Registra mensagens recebidas no histórico
                            if event_type == "on-receive":
                                try:
                                    data = event["data"]
                                    logger.info(f"Processando evento de mensagem recebida: {json.dumps(data, indent=2)}")
                                    
                                    # Extrai a mensagem do payload
                                    message = ""
                                    if "text" in data:
                                        if isinstance(data["text"], dict):
                                            message = data["text"].get("message", "")
                                        else:
                                            message = str(data["text"])
                                    elif "image" in data:
                                        message = f"[Imagem] {data['image'].get('caption', '')}"
                                    elif "video" in data:
                                        message = f"[Vídeo] {data['video'].get('caption', '')}"
                                    elif "audio" in data:
                                        message = "[Áudio]"
                                    elif "document" in data:
                                        message = f"[Documento] {data['document'].get('fileName', '')}"
                                    
                                    if message:
                                        # Formata a mensagem com timestamp
                                        timestamp = datetime.fromtimestamp(data.get("momment", time.time() * 1000) / 1000).strftime("%H:%M:%S")
                                        formatted_msg = f"📱 {data.get('phone')} ({timestamp}): {message}"
                                        
                                        # Atualiza o histórico de mensagens recebidas
                                        current_history = received_history.value if received_history.value else []
                                        new_history = current_history + [(None, formatted_msg)]
                                        received_history.update(value=new_history)
                                        
                                        logger.info(f"Mensagem recebida adicionada ao histórico: {formatted_msg}")
                                except Exception as e:
                                    logger.error(f"Erro ao processar mensagem recebida: {str(e)}")
                                    logger.error(f"Dados do evento: {json.dumps(event, indent=2)}")
                            
                            # Atualiza status de mensagens enviadas
                            elif event_type == "message-status":
                                try:
                                    history_service.update_message_status(
                                        event["data"].get("messageId"),
                                        event["data"].get("status")
                                    )
                                    if phone:
                                        # Atualiza histórico de mensagens enviadas
                                        new_history = load_chat_history(phone)
                                        sent_history.update(value=new_history)
                                except Exception as e:
                                    logger.error(f"Erro ao atualizar status: {str(e)}")
                
                last_update = current_time
                
        except Exception as e:
            logger.error(f"Erro ao monitorar eventos: {str(e)}")
        
        time.sleep(1)
    
    logger.info("🛑 Monitoramento de eventos encerrado")

def stop_server(status: gr.Textbox) -> str:
    """Para o servidor graciosamente"""
    try:
        logger.info("🛑 Parando servidor...")
        stop_event.set()
        
        if poll_thread and poll_thread.is_alive():
            poll_thread.join(timeout=5)
        
        return "✅ Servidor parado com sucesso! Você pode fechar esta janela."
    except Exception as e:
        logger.error(f"Erro ao parar servidor: {str(e)}")
        return f"❌ Erro ao parar servidor: {str(e)}"

def clear_history(phone: str, chat_history: list) -> tuple[str, list]:
    """Limpa o histórico de mensagens"""
    try:
        if not phone:
            return "❌ Por favor, insira um número de telefone primeiro", chat_history
        
        if history_service.clear_chat_history(phone):
            return "✅ Histórico limpo com sucesso!", []
        else:
            return "❌ Erro ao limpar histórico", chat_history
            
    except Exception as e:
        return f"❌ Erro: {str(e)}", chat_history

def create_interface() -> gr.Blocks:
    """Cria a interface Gradio"""
    with gr.Blocks(title="Z-API Chat Interface", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# Z-API Chat Interface")
        
        with gr.Row():
            with gr.Column(scale=2):
                phone = gr.Textbox(
                    label="Número de telefone",
                    placeholder="Ex: 5521999999999",
                    value="5521936182339"
                )
                message = gr.Textbox(
                    label="Mensagem",
                    placeholder="Digite sua mensagem...",
                    value="",
                    lines=3
                )
            
            with gr.Column(scale=1):
                send_btn = gr.Button("📤 Enviar Mensagem", variant="primary")
                clear_btn = gr.Button("🗑️ Limpar Histórico", variant="secondary")
                stop_btn = gr.Button("🛑 Parar Servidor", variant="stop")
                status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=3
                )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📤 Histórico de Mensagens Enviadas")
                sent_history = gr.Chatbot(
                    label="Histórico de Enviadas",
                    height=500,
                    show_label=False
                )
            
            with gr.Column():
                gr.Markdown("### 📥 Histórico de Mensagens Recebidas")
                received_history = gr.Chatbot(
                    label="Histórico de Recebidas",
                    height=500,
                    show_label=False
                )
        
        # Callbacks
        send_btn.click(
            fn=send_message,
            inputs=[phone, message, sent_history],
            outputs=[status, sent_history, message]
        )
        
        clear_btn.click(
            fn=clear_history,
            inputs=[phone, sent_history],
            outputs=[status, sent_history]
        )
        
        stop_btn.click(
            fn=stop_server,
            inputs=[status],
            outputs=[status]
        )
        
        # Atualiza o histórico quando o número muda
        phone.change(
            fn=load_chat_history,
            inputs=[phone],
            outputs=[sent_history]
        )
        
        # Inicia o monitoramento de eventos em background
        global poll_thread
        poll_thread = Thread(
            target=poll_events,
            args=(phone.value, sent_history, received_history),
            daemon=True
        )
        poll_thread.start()
    
    return interface

if __name__ == "__main__":
    try:
        interface = create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Encerrando servidor...")
        stop_event.set()
        if poll_thread:
            poll_thread.join(timeout=5)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        stop_event.set()
        if poll_thread:
            poll_thread.join(timeout=5)
        sys.exit(1) 