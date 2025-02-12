import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from ..models.whatsapp_message import WhatsAppMessage
from ..utils.logger import APILogger
from .integration_service import IntegrationService

logger = APILogger("scheduler")

class MessageScheduler:
    """Serviço para agendamento de mensagens"""
    
    def __init__(self, integration_service: IntegrationService):
        self.integration = integration_service
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._jobs: Dict[str, str] = {}  # job_id -> message_id
        
    def schedule_message(
        self,
        contact_id: str,
        message_text: str,
        schedule_time: datetime
    ) -> str:
        """
        Agenda uma mensagem para envio
        
        Args:
            contact_id: ID do contato
            message_text: Texto da mensagem
            schedule_time: Data/hora para envio
            
        Returns:
            ID do agendamento
        """
        logger.info(f"Agendando mensagem para {contact_id} em {schedule_time}")
        
        job = self.scheduler.add_job(
            func=self._send_scheduled_message,
            trigger=DateTrigger(run_date=schedule_time),
            args=[contact_id, message_text]
        )
        
        logger.info(f"Mensagem agendada com ID {job.id}")
        return job.id
    
    def schedule_recurring_message(
        self,
        contact_id: str,
        message_text: str,
        cron_expression: str
    ) -> str:
        """
        Agenda uma mensagem recorrente
        
        Args:
            contact_id: ID do contato
            message_text: Texto da mensagem
            cron_expression: Expressão cron (ex: "0 9 * * 1-5" para dias úteis às 9h)
            
        Returns:
            ID do agendamento
        """
        logger.info(f"Agendando mensagem recorrente para {contact_id} com cron {cron_expression}")
        
        job = self.scheduler.add_job(
            func=self._send_scheduled_message,
            trigger=CronTrigger.from_crontab(cron_expression),
            args=[contact_id, message_text]
        )
        
        logger.info(f"Mensagem recorrente agendada com ID {job.id}")
        return job.id
    
    def schedule_bulk_message(
        self,
        message_text: str,
        schedule_time: datetime,
        filter_query: Optional[str] = None
    ) -> str:
        """
        Agenda uma mensagem em massa
        
        Args:
            message_text: Texto da mensagem
            schedule_time: Data/hora para envio
            filter_query: Filtro opcional para contatos
            
        Returns:
            ID do agendamento
        """
        logger.info(f"Agendando mensagem em massa para {schedule_time}")
        
        job = self.scheduler.add_job(
            func=self._send_scheduled_bulk_message,
            trigger=DateTrigger(run_date=schedule_time),
            args=[message_text, filter_query]
        )
        
        logger.info(f"Mensagem em massa agendada com ID {job.id}")
        return job.id
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancela um agendamento"""
        try:
            self.scheduler.remove_job(schedule_id)
            logger.info(f"Agendamento {schedule_id} cancelado")
            return True
        except Exception as e:
            logger.error(f"Erro ao cancelar agendamento {schedule_id}: {str(e)}")
            return False
    
    def list_schedules(self) -> List[Dict]:
        """Lista todos os agendamentos ativos"""
        return [
            {
                "id": job.id,
                "next_run_time": job.next_run_time,
                "function": job.func.__name__,
                "args": job.args
            }
            for job in self.scheduler.get_jobs()
        ]
    
    def _send_scheduled_message(self, contact_id: str, message_text: str):
        """Callback para envio de mensagem agendada"""
        try:
            logger.info(f"Enviando mensagem agendada para {contact_id}")
            result = self.integration.send_message_to_contact(
                contact_id=contact_id,
                message_text=message_text
            )
            if result:
                logger.info(f"Mensagem agendada enviada com sucesso: {result.message_id}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem agendada: {str(e)}")
    
    def _send_scheduled_bulk_message(self, message_text: str, filter_query: Optional[str]):
        """Callback para envio de mensagem em massa agendada"""
        try:
            logger.info("Iniciando envio de mensagem em massa agendada")
            results = self.integration.send_bulk_message(
                message_text=message_text,
                filter_query=filter_query
            )
            logger.info(f"Mensagem em massa enviada para {len(results)} contatos")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem em massa agendada: {str(e)}")
    
    def __del__(self):
        """Garante que o scheduler seja desligado"""
        self.scheduler.shutdown() 