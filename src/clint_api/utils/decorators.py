import time
import functools
from typing import Any, Callable, Type, Tuple, Optional
from requests.exceptions import RequestException

from .logger import APILogger

logger = APILogger("decorators")

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (RequestException,)
):
    """
    Decorator para retry em caso de falha
    
    Args:
        max_attempts: Número máximo de tentativas
        delay: Tempo de espera inicial entre tentativas
        backoff: Fator multiplicador do delay a cada tentativa
        exceptions: Tupla de exceções que devem ser tratadas
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Tentativa {attempt + 1} falhou: {str(e)}. "
                            f"Tentando novamente em {current_delay:.1f} segundos..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Todas as {max_attempts} tentativas falharam. "
                            f"Último erro: {str(e)}"
                        )
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

def log_api_call(logger_name: Optional[str] = None):
    """
    Decorator para logging de chamadas de API
    
    Args:
        logger_name: Nome opcional para o logger
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Cria ou obtém logger
            log = APILogger(logger_name or func.__name__)
            
            try:
                # Registra chamada
                log.info(f"Chamando {func.__name__}")
                log.debug(f"Args: {args}, Kwargs: {kwargs}")
                
                # Executa função
                result = func(*args, **kwargs)
                
                # Registra sucesso
                log.info(f"Chamada {func.__name__} concluída com sucesso")
                log.debug(f"Resultado: {result}")
                
                return result
            except Exception as e:
                # Registra erro
                log.log_error(e, {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                })
                raise
        return wrapper
    return decorator 