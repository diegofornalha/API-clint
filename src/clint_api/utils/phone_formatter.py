from typing import Optional

class PhoneFormatter:
    """Classe utilitária para padronização de números de telefone"""
    
    @staticmethod
    def format_to_db(phone: str) -> str:
        """
        Formata o número para armazenamento no banco de dados (sem prefixo 55)
        Exemplo: 5521999999999 -> 21999999999
        """
        # Remove caracteres não numéricos
        phone = "".join(filter(str.isdigit, phone))
        # Remove o prefixo 55 se existir
        if phone.startswith("55") and len(phone) > 2:
            phone = phone[2:]
        return phone
    
    @staticmethod
    def format_to_api(phone: str) -> str:
        """
        Formata o número para envio à API (com prefixo 55)
        Exemplo: 21999999999 -> 5521999999999
        """
        # Remove caracteres não numéricos
        phone = "".join(filter(str.isdigit, phone))
        # Adiciona o prefixo 55 se não existir
        if not phone.startswith("55"):
            phone = "55" + phone
        return phone
    
    @staticmethod
    def is_valid(phone: str) -> bool:
        """
        Verifica se o número é válido
        Regras:
        - Deve ter apenas dígitos
        - Deve ter entre 10 e 11 dígitos (sem prefixo) ou 12 e 13 dígitos (com prefixo)
        - Se tiver prefixo, deve ser 55
        """
        # Remove caracteres não numéricos
        phone = "".join(filter(str.isdigit, phone))
        
        # Verifica o tamanho
        if len(phone) < 10 or len(phone) > 13:
            return False
            
        # Se tiver 12 ou 13 dígitos, deve começar com 55
        if len(phone) >= 12 and not phone.startswith("55"):
            return False
            
        return True
    
    @staticmethod
    def extract_info(phone: str) -> Optional[dict]:
        """
        Extrai informações do número de telefone
        Retorna um dicionário com:
        - ddi: código do país (55 para Brasil)
        - ddd: código de área
        - number: número do telefone
        """
        # Remove caracteres não numéricos
        phone = "".join(filter(str.isdigit, phone))
        
        if not PhoneFormatter.is_valid(phone):
            return None
            
        # Se o número já tem o prefixo 55, remove
        if phone.startswith("55"):
            phone = phone[2:]
            
        # Extrai DDD e número
        ddd = phone[:2]
        number = phone[2:]
        
        return {
            "ddi": "55",  # Sempre 55 para Brasil
            "ddd": ddd,
            "number": number,
            "formatted": {
                "db": f"{ddd}{number}",  # Para banco de dados
                "api": f"55{ddd}{number}",  # Para API
                "display": f"+55 ({ddd}) {number[:5]}-{number[5:]}"  # Para exibição
            }
        } 