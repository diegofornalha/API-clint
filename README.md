# Cliente Python para API Clint

Cliente Python para integração com a [API Clint](https://clint-api.readme.io/reference).

## Instalação

```bash
pip install -r requirements.txt
```

## Estrutura do Projeto

```
API-clint/
├── README.md
├── requirements.txt
├── setup.py
└── src/
    ├── clint_api/           # Pacote principal
    │   ├── __init__.py
    │   ├── clients/         # Implementações dos clientes
    │   ├── models/          # Modelos de dados
    │   ├── exceptions/      # Exceções personalizadas
    │   └── utils/           # Utilitários
    ├── examples/            # Exemplos de uso
    └── tests/               # Testes automatizados
```

## Uso Básico

```python
from clint_api import ContactClient, Contact

# Inicializar o cliente
client = ContactClient(api_token="seu_token_aqui")

# Criar um contato
contact = Contact(
    name="João da Silva",
    ddi="+55",
    phone="11999999999",
    email="joao@example.com",
    username="joaosilva"
)
created = client.create_contact(contact)

# Buscar um contato
contact = client.get_contact(created.id)

# Atualizar um contato
contact.name = "João Silva"
updated = client.update_contact(contact)

# Deletar um contato
client.delete_contact(contact.id)

# Listar contatos (com paginação)
contacts = client.list_contacts(page=1, limit=10)

# Buscar contatos
results = client.search_contacts(query="João")
```

## Exemplos via HTTPie

### Criar Contato
```bash
http POST 'https://api.clint.digital/v1/contacts' \
    api-token:'seu_token_aqui' \
    name='João da Silva' \
    ddi='+55' \
    phone='11999999999' \
    email='joao@example.com' \
    username='joaosilva' \
    fields:='{"organization": {"department": "TI"}}'
```

### Buscar Contato
```bash
http GET 'https://api.clint.digital/v1/contacts/{id}' \
    api-token:'seu_token_aqui'
```

### Atualizar Contato
```bash
http PUT 'https://api.clint.digital/v1/contacts/{id}' \
    api-token:'seu_token_aqui' \
    name='João Silva' \
    ddi='+55' \
    phone='11999999999' \
    email='joao@example.com' \
    username='joaosilva'
```

### Deletar Contato
```bash
http DELETE 'https://api.clint.digital/v1/contacts/{id}' \
    api-token:'seu_token_aqui'
```

## Documentação Completa

Para mais detalhes sobre a API, consulte a [documentação oficial](https://clint-api.readme.io/reference).

## Desenvolvimento

### Configuração do Ambiente

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/API-clint.git
cd API-clint
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Execute os testes
```bash
python -m pytest tests/
```

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes. 