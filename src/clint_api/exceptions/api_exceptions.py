class ClintAPIException(Exception):
    """Exceção base para erros da API Clint"""
    pass

class ContactNotFoundException(ClintAPIException):
    """Exceção lançada quando um contato não é encontrado"""
    pass

class ContactAlreadyExistsException(ClintAPIException):
    """Exceção lançada quando tenta criar um contato com email duplicado"""
    pass

class APIAuthenticationError(ClintAPIException):
    """Exceção lançada quando há problemas de autenticação"""
    pass 