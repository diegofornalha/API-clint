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
        
        # Cria diretório de logs se não existir
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(
            filename=log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatação
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Formata dicionário para log"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def log_request(self, method: str, url: str, headers: Dict[str, str], data: Any = None):
        """Registra uma requisição"""
        message = f"\nRequest: {method} {url}\nHeaders: {self._format_dict(headers)}"
        if data:
            message += f"\nData: {self._format_dict(data) if isinstance(data, dict) else str(data)}"
        self.logger.debug(message)
    
    def log_response(self, status_code: int, response_data: Any):
        """Registra uma resposta"""
        message = f"\nResponse Status: {status_code}\nData: {self._format_dict(response_data) if isinstance(response_data, dict) else str(response_data)}"
        self.logger.debug(message)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Registra um erro com contexto"""
        message = f"\nError: {str(error)}"
        if context:
            message += f"\nContext: {self._format_dict(context)}"
        self.logger.error(message, exc_info=True)
    
    def info(self, message: str):
        """Registra uma mensagem informativa"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Registra um aviso"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Registra uma mensagem de debug"""
        self.logger.debug(message)

    def error(self, message: str):
        """Registra uma mensagem de erro"""
        self.logger.error(message) 