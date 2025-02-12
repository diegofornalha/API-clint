from clint_api.services.integration_service import IntegrationService

def main():
    # Configurações
    CLINT_TOKEN = "U2FsdGVkX18W3nY0vuDyNxG7fMfa7aEnkkhA/uBC2WtNtrs48PkAHFdgXSLIythxoDie6/WUsB4paq4QSsKeTQ=="
    ZAPI_INSTANCE = "SEU_INSTANCE_ID"  # Substitua pelo seu Instance ID do Z-API
    ZAPI_TOKEN = "SEU_TOKEN_ZAPI"      # Substitua pelo seu Token do Z-API
    
    # Cria o serviço de integração
    service = IntegrationService(
        clint_token=CLINT_TOKEN,
        zapi_instance_id=ZAPI_INSTANCE,
        zapi_token=ZAPI_TOKEN
    )
    
    try:
        # Exemplo 1: Enviar mensagem para um contato específico
        contact_id = "ID_DO_CONTATO"  # Substitua pelo ID do contato
        message = "Olá! Esta é uma mensagem de teste via integração Clint API + Z-API."
        
        result = service.send_message_to_contact(contact_id, message)
        if result:
            print(f"Mensagem enviada com sucesso! ID: {result.message_id}")
            print(f"Status: {result.status}")
        
        # Exemplo 2: Enviar mensagem em massa para contatos que contém "Silva" no nome
        bulk_message = "Olá! Esta é uma mensagem em massa via integração."
        results = service.send_bulk_message(
            message_text=bulk_message,
            filter_query="Silva"
        )
        
        print(f"\nMensagens em massa enviadas: {len(results)}")
        for msg in results:
            print(f"- Mensagem {msg.message_id}: {msg.status}")
            
    except Exception as e:
        print(f"Erro durante a integração: {str(e)}")

if __name__ == "__main__":
    main() 