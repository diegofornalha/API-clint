from datetime import datetime, timedelta
from clint_api.services.integration_service import IntegrationService
from clint_api.services.scheduler_service import MessageScheduler
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.config import Config
from clint_api.utils.logger import APILogger

logger = APILogger("example")

def main():
    # Valida configurações
    error = Config.validate()
    if error:
        logger.error(f"Erro de configuração: {error}")
        return
    
    # Cria os serviços usando as configurações do .env
    integration = IntegrationService(
        clint_token=Config.CLINT_API_TOKEN,
        zapi_instance_id=Config.ZAPI_INSTANCE_ID,
        zapi_token=Config.ZAPI_TOKEN
    )
    scheduler = MessageScheduler(integration)
    
    try:
        # Exemplo 1: Enviar imagem para um contato
        contact_id = "ID_DO_CONTATO"  # Substitua pelo ID do contato
        message = WhatsAppMessage(
            phone="5511999999999",  # Será substituído pelo telefone do contato
            message="Veja nossa nova logo!",
            instance_id=Config.ZAPI_INSTANCE_ID,
            token=Config.ZAPI_TOKEN,
            message_type=MessageType.IMAGE,
            media_url="https://exemplo.com/logo.png",
            caption="Nossa nova identidade visual"
        )
        
        result = integration.send_message_to_contact(contact_id, message)
        if result:
            logger.info(f"Imagem enviada com sucesso! ID: {result.message_id}")
            logger.info(f"Status: {result.status}")
        
        # Exemplo 2: Agendar mensagem recorrente
        schedule_id = scheduler.schedule_recurring_message(
            contact_id=contact_id,
            message_text="Bom dia! Lembre-se de verificar suas tarefas.",
            cron_expression="0 9 * * 1-5"  # Segunda a sexta às 9h
        )
        logger.info(f"Mensagem recorrente agendada com ID: {schedule_id}")
        
        # Exemplo 3: Agendar mensagem em massa para daqui 1 hora
        schedule_time = datetime.now() + timedelta(hours=1)
        bulk_id = scheduler.schedule_bulk_message(
            message_text="Promoção especial! Aproveite!",
            schedule_time=schedule_time,
            filter_query="Silva"  # Opcional: filtrar contatos
        )
        logger.info(f"Mensagem em massa agendada com ID: {bulk_id}")
        
        # Exemplo 4: Listar agendamentos
        schedules = scheduler.list_schedules()
        logger.info("\nAgendamentos ativos:")
        for schedule in schedules:
            logger.info(f"- ID: {schedule['id']}")
            logger.info(f"  Próxima execução: {schedule['next_run_time']}")
            logger.info(f"  Função: {schedule['function']}")
            logger.info(f"  Argumentos: {schedule['args']}")
        
        # Exemplo 5: Cancelar um agendamento
        if scheduler.cancel_schedule(schedule_id):
            logger.info(f"\nAgendamento {schedule_id} cancelado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main() 