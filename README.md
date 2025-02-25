# Cliente Python para API Clint

Cliente Python para integração com a [API Clint](https://clint-api.readme.io/reference).

## Novidades

### Interface Streamlit para Envio de Mensagens via WhatsApp

Adicionamos uma interface gráfica usando Streamlit para facilitar o envio de mensagens e áudios via WhatsApp utilizando a Z-API.

#### Funcionalidades principais

- **Interface amigável**: Fácil configuração de credenciais e visualização de resultados
- **Envio de áudio**: Upload de arquivos nos formatos MP3, WAV, OGG
- **Envio de texto**: Mensagens de texto simples
- **Modos de envio**:
  - Individual: para um único número
  - Em massa: para múltiplos números separados por vírgula
  - Importação de números: carregamento de lista de números a partir de arquivo de texto
- **Configurações salvas**: Todos os parâmetros podem ser salvos em arquivo .env
- **Validação de conexão**: Teste de conectividade com a Z-API

#### Limitações atuais

- A conversão de texto para áudio via gTTS está temporariamente desativada
- Arquivos de áudio devem ser enviados diretamente no formato suportado

#### Para executar a interface:

```bash
streamlit run streamlit_audio_interface.py --server.port=8502
```

Acesse: http://localhost:8502

#### Formato para números no arquivo de texto

Para envio em massa usando arquivo de texto, cada número deve estar em uma linha separada com formato:
```
5521999999999
5511888888888
```
Incluindo DDI e DDD, sem caracteres especiais.

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
├── .env.example        # Modelo para configurações
└── src/
    ├── clint_api/           # Pacote principal
    │   ├── __init__.py
    │   ├── clients/         # Implementações dos clientes
    │   ├── models/          # Modelos de dados
    │   ├── exceptions/      # Exceções personalizadas
    │   ├── services/        # Serviços de negócio
    │   ├── webhooks/        # Handlers de webhooks
    │   └── utils/           # Utilitários
    │       ├── config.py    # Configurações centralizadas
    │       └── zapi_helpers.py # Funções auxiliares para Z-API
    ├── examples/            # Exemplos de uso
    │   ├── clint-scripts/   # Exemplos específicos da API Clint
    │   └── z-api-scripts/   # Exemplos específicos da Z-API
    └── tests/               # Testes automatizados
```

## Configuração Inicial

1. Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e preencha as variáveis necessárias:
```
# API Clint
CLINT_API_TOKEN=seu_token_aqui

# Z-API
ZAPI_INSTANCE_ID=seu_instance_id_aqui
ZAPI_TOKEN=seu_token_aqui
ZAPI_SECURITY_TOKEN=seu_security_token_aqui

# Outros valores necessários...
```

3. Execute os exemplos para testar a configuração:
```bash
python src/examples/clint-scripts/list_clint_contacts.py
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

## Fluxos Completos

Esta seção descreve os fluxos completos de integração do início ao fim.

### 1. Fluxo Completo de Contatos

O fluxo de trabalho com contatos envolve as seguintes etapas:

#### 1.1 Criar e gerenciar contatos na API Clint

```python
from clint_api.clients.contact_client import ContactClient
from clint_api.models.contact import Contact
from clint_api.utils.config import Config

# 1. Inicializar o cliente
client = ContactClient(Config.CLINT_API_TOKEN)

# 2. Criar um contato
contact = Contact(
    name="João da Silva",
    ddi="+55",
    phone="11999999999",
    email="joao@example.com",
    username="joaosilva"
)
created_contact = client.create_contact(contact)
print(f"Contato criado com ID: {created_contact.id}")

# 3. Atualizar o contato
created_contact.name = "João Atualizado"
updated_contact = client.update_contact(created_contact)
print(f"Contato atualizado: {updated_contact.name}")

# 4. Buscar contatos por critérios
contacts = client.search_contacts(name="João")
for c in contacts:
    print(f"Encontrado: {c.name} - {c.phone}")
```

### 2. Fluxo de Mensagens via WhatsApp (Z-API)

#### 2.1 Configuração inicial da Z-API

Antes de enviar mensagens, você precisa:

1. Ter uma conta na Z-API (https://app.z-api.io)
2. Criar uma instância e obter o ID, Token e Security Token
3. Conectar a instância com um número de WhatsApp
4. Configurar as credenciais em seu arquivo `.env`

#### 2.2 Envio de mensagens de texto simples

```python
from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.config import Config

# 1. Inicializar o cliente Z-API
client = ZAPIClient(
    instance_id=Config.ZAPI_INSTANCE_ID,
    token=Config.ZAPI_TOKEN,
    security_token=Config.ZAPI_SECURITY_TOKEN
)

# 2. Verificar se está conectado
if not client.is_connected():
    print("WhatsApp não está conectado! Conecte através do aplicativo Z-API.")
    exit()

# 3. Criar e enviar uma mensagem simples
message = WhatsAppMessage(
    phone="5511999999999",  # Número de destino
    message="Olá! Esta é uma mensagem de teste.",
    message_type=MessageType.TEXT
)
result = client.send_message(message)

# 4. Verificar resultado
if result and result.message_id:
    print(f"Mensagem enviada com sucesso! ID: {result.message_id}")
else:
    print("Falha ao enviar mensagem.")
```

#### 2.3 Envio de mensagens com mídia

```python
from clint_api.clients.zapi_client import ZAPIClient
from clint_api.models.whatsapp_message import WhatsAppMessage, MessageType
from clint_api.utils.config import Config

# 1. Inicializar o cliente
client = ZAPIClient(
    instance_id=Config.ZAPI_INSTANCE_ID,
    token=Config.ZAPI_TOKEN,
    security_token=Config.ZAPI_SECURITY_TOKEN
)

# 2. Enviar imagem
image_message = WhatsAppMessage(
    phone="5511999999999",
    message="Veja nossa imagem",
    message_type=MessageType.IMAGE,
    media_url=Config.MEDIA_URLS['image'],
    caption="Legenda da imagem"
)
image_result = client.send_message(image_message)

# 3. Enviar documento
document_message = WhatsAppMessage(
    phone="5511999999999",
    message="Documento importante",
    message_type=MessageType.DOCUMENT,
    media_url=Config.MEDIA_URLS['document'],
    caption="Documento PDF"
)
document_result = client.send_message(document_message)
```

### 3. Fluxo de Webhooks (Recebimento de Mensagens)

#### 3.1 Configuração de Webhooks

Os webhooks permitem receber notificações de eventos da Z-API, como mensagens recebidas.

```python
from clint_api.utils.zapi_helpers import configure_webhooks
from clint_api.utils.config import Config

# 1. Configurar webhooks (use sua URL pública)
webhook_url = "https://seu-dominio-público.com"
results = configure_webhooks(
    instance_id=Config.ZAPI_INSTANCE_ID,
    token=Config.ZAPI_TOKEN,
    security_token=Config.ZAPI_SECURITY_TOKEN,
    base_url=webhook_url
)

# Ou para teste local com Localtunnel:
from clint_api.utils.zapi_helpers import start_localtunnel, configure_webhooks

# 2. Iniciar um tunnel para sua porta local
tunnel_url = start_localtunnel(port=8000)
if tunnel_url:
    configure_webhooks(
        instance_id=Config.ZAPI_INSTANCE_ID,
        token=Config.ZAPI_TOKEN,
        security_token=Config.ZAPI_SECURITY_TOKEN,
        base_url=tunnel_url
    )
```

#### 3.2 Processamento de Webhooks

Para processar webhooks, você precisa de um servidor HTTP. Um exemplo com FastAPI:

```python
from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/webhooks/zapi/on-receive")
async def webhook_on_receive(request: Request):
    """Webhook para mensagens recebidas"""
    try:
        # Validar token
        client_token = request.headers.get("Client-Token")
        if client_token != Config.ZAPI_SECURITY_TOKEN:
            return {"status": "error", "message": "Invalid token"}
            
        # Processar dados
        data = await request.json()
        
        # Extrair informações relevantes
        sender = data.get("phone", "")
        message_text = ""
        
        if "text" in data:
            message_text = data["text"].get("message", "")
        elif "image" in data:
            message_text = f"[Imagem] {data['image'].get('caption', '')}"
        
        # Aqui você pode salvar a mensagem ou processá-la conforme necessário
        print(f"Mensagem de {sender}: {message_text}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

# Iniciar o servidor
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Fluxo de Integração Completo

O fluxo de integração completo combina a gestão de contatos com o envio de mensagens:

```python
from clint_api.services.integration_service import IntegrationService
from clint_api.utils.config import Config

# 1. Inicializar o serviço de integração
service = IntegrationService(
    clint_token=Config.CLINT_API_TOKEN,
    zapi_instance_id=Config.ZAPI_INSTANCE_ID,
    zapi_token=Config.ZAPI_TOKEN
)

# 2. Buscar um contato específico
contact = service.contact_client.get_contact_by_phone("11999999999")

# 3. Enviar mensagem para o contato
if contact:
    result = service.send_message_to_contact(
        contact_id=contact.id,
        message_text="Olá! Mensagem de teste via integração."
    )
    print(f"Mensagem enviada: {result.status}")

# 4. Enviar mensagens em massa para um grupo de contatos
results = service.send_bulk_message(
    message_text="Promoção especial para todos os clientes!",
    filter_query="São Paulo"  # Filtro opcional para contatos
)
print(f"Mensagens enviadas: {len(results)}")
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

## Interface Streamlit

O projeto agora inclui uma interface web interativa construída com Streamlit para facilitar o envio de mensagens de áudio via WhatsApp.

### Instalação do Streamlit

Certifique-se de ter o Streamlit instalado:

```bash
pip install streamlit
```

Ou simplesmente instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

### Executando a Interface

Para iniciar a interface Streamlit, execute:

```bash
streamlit run streamlit_audio_interface.py
```

Isso iniciará um servidor local e abrirá a interface no seu navegador padrão.

### Funcionalidades

- Upload de arquivos de áudio (MP3, WAV, OGG)
- Envio direto para contatos do WhatsApp
- Feedback visual sobre o status do envio
- Interface intuitiva e responsiva
- **Configuração via Interface**: Configure suas credenciais da Z-API diretamente pela interface, sem precisar editar arquivos manualmente
- **Envio em Massa**: Envie mensagens para múltiplos números de uma só vez, separando-os por vírgula

### Configurando via Interface

A interface Streamlit permite configurar suas credenciais da Z-API diretamente:

1. Acesse a barra lateral clicando no ícone "⚙️" no canto superior direito
2. Expanda a seção "Configuração da API Z-API"
3. Preencha seus dados de:
   - Instance ID
   - Token
   - Security Token
   - Número do Remetente
4. Clique em "Salvar Configuração"

Suas configurações serão salvas e persistirão entre as sessões.

### Enviando Áudios em Massa

Para enviar áudios para múltiplos destinatários:

1. Acesse a aba "📢 Envio em Massa"
2. Carregue o arquivo de áudio desejado
3. Digite os números de telefone separados por vírgula
   ```
   5521999999999, 5531888888888, 5511777777777
   ```
4. Clique em "Enviar para Todos"
5. Acompanhe o progresso e o resultado individual de cada envio

### Testando a Interface

Para verificar se a instalação foi bem-sucedida e testar a funcionalidade básica, execute:

```bash
python test_streamlit_interface.py
```

Este script verificará:
1. Se o Streamlit está instalado corretamente
2. Se o arquivo da interface existe
3. Se as funções de codificação de áudio estão funcionando

## Migração de Gradio para Streamlit

Este projeto passou por uma migração da interface Gradio para Streamlit. Para mais detalhes sobre o processo de migração e o status atual, consulte o arquivo [MIGRATION.md](MIGRATION.md). 