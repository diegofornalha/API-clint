from clint_api.services.message_history_service import MessageHistoryService
from clint_api.models.message_history import MessageDirection, MessageHistory
import time
from datetime import datetime, timedelta

def main():
    """Monitora mensagens recebidas em tempo real"""
    history_service = MessageHistoryService()
    last_check = datetime.now() - timedelta(minutes=5)  # Começa verificando os últimos 5 minutos
    
    print("\n🔍 Monitorando mensagens recebidas...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            # Obtém todas as mensagens
            messages = history_service.session.query(MessageHistory)\
                .filter(MessageHistory.timestamp > last_check)\
                .filter(MessageHistory.direction == MessageDirection.RECEIVED)\
                .order_by(MessageHistory.timestamp.desc())\
                .all()
            
            # Atualiza timestamp da última verificação
            last_check = datetime.now()
            
            # Exibe mensagens encontradas
            for msg in messages:
                print(f"📱 Nova mensagem recebida:")
                print(f"   De: {msg.phone}")
                print(f"   Mensagem: {msg.message}")
                print(f"   Horário: {msg.timestamp.strftime('%H:%M:%S')}")
                print(f"   ID: {msg.message_id}")
                print("-" * 50)
            
            # Aguarda 2 segundos antes da próxima verificação
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoramento encerrado!")

if __name__ == "__main__":
    main() 