# Manager Events

Uma aplicação moderna em Streamlit para gerenciar lançamentos e eventos, com integração ao Google Calendar.

## 🌟 Características

- 🌙 Interface moderna com tema escuro
- 📊 Dashboard com visualizações interativas
- 📅 Integração com Google Calendar
- 🔍 Filtros avançados
- 📱 Design responsivo
- 🎨 Gráficos interativos com Plotly

## 🚀 Deploy

### Pré-requisitos

1. Conta no GitHub
2. Conta no [Streamlit Cloud](https://share.streamlit.io)
3. Credenciais do Google Calendar API (`credentials.json`)

### Passos para Deploy

1. Faça login no [Streamlit Cloud](https://share.streamlit.io)
2. Clique em "New app"
3. Selecione este repositório
4. Configure:
   - Main file path: `app.py`
   - Python version: 3.9

### Configuração dos Secrets

No Streamlit Cloud, você precisa configurar os secrets do Google Calendar:

1. Vá em ⚙️ Settings do seu app
2. Na seção "Secrets", adicione:
```toml
[gcp_service_account]
type = "service_account"
project_id = "seu-projeto-id"
private_key_id = "sua-private-key-id"
private_key = "sua-private-key"
client_email = "seu-client-email"
client_id = "seu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "sua-cert-url"
```

## 💻 Desenvolvimento Local

1. Clone o repositório:
```bash
git clone https://github.com/orealisaque/Manager-Events.git
cd Manager-Events
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais do Google Calendar:
- Coloque o arquivo `credentials.json` na raiz do projeto

4. Execute a aplicação:
```bash
streamlit run app.py
```

## 📝 Licença

Este projeto está sob a licença MIT.

## Funcionalidades

### Dashboard
- Visualização da distribuição de status dos lançamentos
- Gráfico de temperatura dos eventos
- Visão geral dos próximos eventos

### Adicionar Lançamento
- Formulário intuitivo para adicionar novos eventos
- Integração automática com Google Calendar
- Campos para nome, data, links e status

### Visualizar Lançamentos
- Lista completa de todos os lançamentos
- Filtros por status, temperatura e data
- Visualização em tabela com formatação personalizada

## Contribuição

Sinta-se à vontade para contribuir com o projeto através de pull requests ou reportando issues.
