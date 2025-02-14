import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

class APILogger:
    """Logger personalizado para APIs"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Data atual para organização das pastas
        current_date = datetime.now()
        self.date_str = current_date.strftime('%Y%m%d')
        self.time_str = current_date.strftime('%H%M%S')
        
        # Determina se é um log relacionado a mensagens ou Z-API
        is_message_log = any(x in name.lower() for x in ['message', 'msg', 'send_', 'receive_'])
        is_zapi_log = 'zapi' in name.lower()
        
        # Todos os logs relacionados a mensagens ou Z-API vão para mensagens-logs
        if is_message_log or is_zapi_log:
            self.log_base = Path('mensagens-logs')
            # Determina a subcategoria
            if 'test' in name.lower():
                self.category = 'testes'
            elif 'zapi' in name.lower():
                self.category = 'zapi'
            elif 'webhook' in name.lower():
                self.category = 'webhooks'
            else:
                self.category = 'geral'
        else:
            # Para outros tipos de logs, mantém a estrutura original
            self.log_base = Path(log_dir)
            if 'test' in name.lower():
                self.category = 'tests'
            elif 'webhook' in name.lower():
                self.category = 'webhooks'
            else:
                self.category = 'general'
        
        # Cria diretório base de logs se não existir
        self.log_base.mkdir(parents=True, exist_ok=True)
            
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatação
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(self.formatter)
        
        # Adiciona handler de console
        self.logger.addHandler(console_handler)
        
        # Flag para controlar se o arquivo já foi criado
        self._file_handler = None
        self.name = name
        self.is_message_or_zapi_log = is_message_log or is_zapi_log
        
    def _ensure_file_handler(self):
        """Garante que o file handler existe, criando-o se necessário"""
        if self._file_handler is None:
            # Estrutura de diretórios
            if self.is_message_or_zapi_log:
                # Para logs de mensagens e Z-API:
                # mensagens-logs/
                #   └── YYYYMMDD/
                #       └── HHMMSS/
                #           └── categoria/
                #               └── nome_do_log.log
                day_dir = self.log_base / self.date_str
                day_dir.mkdir(exist_ok=True)
                
                time_dir = day_dir / self.time_str
                time_dir.mkdir(exist_ok=True)
                
                category_dir = time_dir / self.category
                category_dir.mkdir(exist_ok=True)
                
                log_file = category_dir / f"{self.name}_{self.date_str}_{self.time_str}.log"
            else:
                # Para outros logs mantém a estrutura original
                category_dir = self.log_base / self.category
                category_dir.mkdir(exist_ok=True)
                log_file = category_dir / f"{self.name}_{self.date_str}.log"
            
            # Cria o file handler
            self._file_handler = logging.FileHandler(
                filename=str(log_file),
                encoding='utf-8'
            )
            self._file_handler.setLevel(logging.DEBUG)
            self._file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self._file_handler)
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Formata dicionário para log"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def log_request(self, method: str, url: str, headers: Dict[str, str], data: Any = None):
        """Registra uma requisição"""
        self._ensure_file_handler()
        message = f"\nRequest: {method} {url}\nHeaders: {self._format_dict(headers)}"
        if data:
            message += f"\nData: {self._format_dict(data) if isinstance(data, dict) else str(data)}"
        self.logger.debug(message)
    
    def log_response(self, status_code: int, response_data: Any):
        """Registra uma resposta"""
        self._ensure_file_handler()
        message = f"\nResponse Status: {status_code}\nData: {self._format_dict(response_data) if isinstance(response_data, dict) else str(response_data)}"
        self.logger.debug(message)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Registra um erro com contexto"""
        self._ensure_file_handler()
        message = f"\nError: {str(error)}"
        if context:
            message += f"\nContext: {self._format_dict(context)}"
        self.logger.error(message, exc_info=True)
    
    def info(self, message: str):
        """Registra uma mensagem informativa"""
        self._ensure_file_handler()
        self.logger.info(message)
    
    def warning(self, message: str):
        """Registra um aviso"""
        self._ensure_file_handler()
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Registra uma mensagem de debug"""
        self._ensure_file_handler()
        self.logger.debug(message)

    def error(self, message: str):
        """Registra uma mensagem de erro"""
        self._ensure_file_handler()
        self.logger.error(message) 