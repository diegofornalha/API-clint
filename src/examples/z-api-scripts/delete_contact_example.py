from clint_api.clients.contact_client import ContactClient
from clint_api.exceptions.api_exceptions import ContactNotFoundException

def main():
    # Token de exemplo (substitua pelo seu token real)
    API_TOKEN = "U2FsdGVkX18W3nY0vuDyNxG7fMfa7aEnkkhA/uBC2WtNtrs48PkAHFdgXSLIythxoDie6/WUsB4paq4QSsKeTQ=="
    
    # Lista de IDs dos contatos para deletar
    CONTACT_IDS = [
        "4c028ada-df82-4a34-ac7f-4de90727fc84",
        "ab2d324f-44ea-46f3-bb67-f392a488e998",
        "e126143a-a9d2-41da-8fa2-26038cff9af8",
        "eb1531ca-cf42-4b80-999b-ee2ace16272a"
    ]
    
    # Criando uma instância do cliente
    client = ContactClient(API_TOKEN)
    
    # Tenta deletar cada contato
    for contact_id in CONTACT_IDS:
        try:
            if client.delete_contact(contact_id):
                print(f"Contato {contact_id} removido com sucesso!")
        except ContactNotFoundException:
            print(f"Contato {contact_id} não encontrado.")
        except Exception as e:
            print(f"Erro ao deletar contato {contact_id}: {str(e)}")

if __name__ == "__main__":
    main() 