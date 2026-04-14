# API e Integrações

## Visão Geral da API

O DevStationPlatform oferece uma API RESTful completa para integração com sistemas externos, automação de processos e desenvolvimento de aplicações clientes.

### Características da API

- **RESTful**: Segue princípios REST com recursos bem definidos
- **Autenticação JWT**: Tokens seguros com expiração configurável
- **Documentação Swagger/OpenAPI**: Documentação automática da API
- **Versionamento**: Suporte a múltiplas versões da API
- **Rate Limiting**: Limitação de requisições por segurança
- **CORS**: Suporte a Cross-Origin Resource Sharing

## Endpoints Principais

### Autenticação

#### POST `/api/v1/auth/login`
Autentica um usuário e retorna token JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "senha123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@devstation.com",
    "full_name": "Administrador",
    "profiles": ["admin", "supervisor"]
  }
}
```

#### POST `/api/v1/auth/refresh`
Renova token de acesso usando refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### POST `/api/v1/auth/logout`
Invalida token atual.

### Usuários

#### GET `/api/v1/users`
Lista usuários (requer permissão `users.read`).

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `per_page`: Itens por página (padrão: 20)
- `search`: Busca por username, email ou nome
- `is_active`: Filtrar por status ativo

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@devstation.com",
      "full_name": "Administrador",
      "is_active": true,
      "created_at": "2026-04-14T10:30:00Z",
      "profiles": ["admin", "supervisor"]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

#### POST `/api/v1/users`
Cria novo usuário (requer permissão `users.create`).

**Request:**
```json
{
  "username": "novousuario",
  "email": "novo@devstation.com",
  "full_name": "Novo Usuário",
  "password": "SenhaSegura123!",
  "profiles": ["user"]
}
```

#### GET `/api/v1/users/{id}`
Obtém detalhes de um usuário específico.

#### PUT `/api/v1/users/{id}`
Atualiza usuário.

#### DELETE `/api/v1/users/{id}`
Desativa usuário (soft delete).

### Perfis e Permissões

#### GET `/api/v1/profiles`
Lista perfis disponíveis.

#### POST `/api/v1/profiles`
Cria novo perfil.

**Request:**
```json
{
  "code": "analista_dados",
  "name": "Analista de Dados",
  "description": "Perfil para análise de dados",
  "parent_profiles": ["user"],
  "permissions": ["data.read", "reports.generate"]
}
```

#### GET `/api/v1/permissions`
Lista todas as permissões do sistema.

### Transações

#### GET `/api/v1/transactions`
Lista transações disponíveis para o usuário atual.

#### POST `/api/v1/transactions/{code}/execute`
Executa uma transação.

**Request:**
```json
{
  "parameters": {
    "query": "SELECT * FROM users WHERE is_active = true",
    "database": "main",
    "max_rows": 100
  }
}
```

**Response:**
```json
{
  "transaction_code": "DS_QUERY",
  "status": "completed",
  "result": {
    "data": [...],
    "columns": ["id", "username", "email"],
    "row_count": 45,
    "execution_time": 0.125
  },
  "transaction_log_id": 12345,
  "executed_at": "2026-04-14T10:35:00Z"
}
```

#### GET `/api/v1/transactions/logs`
Consulta logs de transações executadas.

### Auditoria

#### GET `/api/v1/audit/logs`
Consulta logs de auditoria.

**Query Parameters:**
- `user_id`: Filtrar por usuário
- `action`: Filtrar por tipo de ação
- `resource_type`: Filtrar por tipo de recurso
- `start_date`: Data inicial
- `end_date`: Data final

#### GET `/api/v1/audit/logs/{id}`
Obtém detalhes de um log específico.

### Plugins

#### GET `/api/v1/plugins`
Lista plugins instalados.

#### POST `/api/v1/plugins/install`
Instala novo plugin.

**Request (multipart/form-data):**
- `plugin_file`: Arquivo .zip do plugin
- `config`: Configuração opcional em JSON

#### DELETE `/api/v1/plugins/{name}`
Remove plugin.

## Autenticação e Autorização

### Headers de Autenticação

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Key: sua_chave_api_opcional
```

### Scopes e Permissões

Cada endpoint requer permissões específicas. A API valida automaticamente:

1. **Validade do Token**: Verifica assinatura e expiração
2. **Permissões do Usuário**: Verifica se usuário tem permissão necessária
3. **Contexto da Transação**: Para transações, valida parâmetros e acesso

### Rate Limiting

- **Limite padrão**: 100 requisições por minuto por IP
- **Limite autenticado**: 1000 requisições por minuto por usuário
- **Headers de resposta**:
  ```http
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 997
  X-RateLimit-Reset: 1618317040
  ```

## Webhooks

### Configuração de Webhooks

O sistema pode notificar endpoints externos sobre eventos importantes:

```yaml
webhooks:
  user_created:
    url: "https://seu-sistema.com/webhooks/user-created"
    secret: "seu_segredo_assinatura"
    events: ["user.created", "user.updated"]
  
  transaction_completed:
    url: "https://seu-sistema.com/webhooks/transaction"
    secret: "outro_segredo"
    events: ["transaction.completed", "transaction.failed"]
```

### Payload do Webhook

```json
{
  "event": "user.created",
  "timestamp": "2026-04-14T10:30:00Z",
  "data": {
    "user_id": 123,
    "username": "novousuario",
    "email": "novo@devstation.com"
  },
  "signature": "sha256=..."
}
```

### Validação de Assinatura

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

## SDKs e Bibliotecas Cliente

### Python SDK

```python
from devstation_sdk import DevStationClient

# Inicialização
client = DevStationClient(
    base_url="https://devstation.example.com",
    api_key="sua_chave_api"
)

# Autenticação
token = client.auth.login("username", "password")

# Executar transação
result = client.transactions.execute(
    code="DS_QUERY",
    parameters={"query": "SELECT * FROM users"}
)

# Consultar logs
logs = client.audit.get_logs(
    start_date="2026-04-01",
    end_date="2026-04-14"
)
```

### JavaScript/TypeScript SDK

```typescript
import { DevStationClient } from '@devstation/sdk';

const client = new DevStationClient({
  baseUrl: 'https://devstation.example.com',
  apiKey: 'sua_chave_api'
});

// Autenticação
const token = await client.auth.login('username', 'password');

// Executar transação
const result = await client.transactions.execute('DS_QUERY', {
  query: 'SELECT * FROM users'
});
```

## Integração com Sistemas Externos

### Banco de Dados Externo

```python
# Configuração de conexão externa
external_db_config = {
    "name": "external_sales",
    "type": "postgresql",
    "host": "sales-db.example.com",
    "port": 5432,
    "database": "sales",
    "username": "${EXTERNAL_DB_USER}",
    "password": "${EXTERNAL_DB_PASS}",
    "ssl": true
}

# Uso em transação
transaction_params = {
    "database": "external_sales",
    "query": "SELECT * FROM orders WHERE date >= '2026-04-01'"
}
```

### API de Terceiros

```python
# Configuração de API externa
external_api_config = {
    "name": "payment_gateway",
    "base_url": "https://api.payment.com/v1",
    "auth_type": "bearer_token",
    "token": "${PAYMENT_API_TOKEN}",
    "timeout": 30
}

# Chamada à API externa
response = await client.integrations.call_api(
    api_name="payment_gateway",
    endpoint="/payments",
    method="POST",
    data={"amount": 100.00, "currency": "BRL"}
)
```

## WebSocket para Tempo Real

### Conexão WebSocket

```javascript
const ws = new WebSocket('wss://devstation.example.com/ws');

ws.onopen = () => {
  // Autenticar
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'seu_token_jwt'
  }));
  
  // Inscrever em eventos
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['transactions', 'audit']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evento recebido:', data);
};
```

### Eventos Disponíveis

- `transaction.started`: Transação iniciada
- `transaction.completed`: Transação concluída
- `transaction.failed`: Transação falhou
- `audit.log_created`: Novo log de auditoria
- `user.logged_in`: Usuário autenticado
- `user.logged_out`: Usuário desconectado

## Exportação de Dados

### Formatos Suportados

```python
# Exportar dados em diferentes formatos
csv_data = client.export.csv(
    resource="users",
    filters={"is_active": True}
)

excel_data = client.export.excel(
    resource="transaction_logs",
    columns=["id", "transaction_code", "user", "status"],
    start_date="2026-04-01"
)

pdf_report = client.export.pdf(
    template="monthly_report",
    parameters={"month": 4, "year": 2026}
)
```

### Agendamento de Exportações

```yaml
export_schedules:
  daily_users:
    resource: "users"
    format: "csv"
    filters:
      is_active: true
    schedule: "0 2 * * *"  # 2 AM daily
    destination:
      type: "s3"
      bucket: "devstation-exports"
      path: "users/daily/{date}.csv"
  
  weekly_audit:
    resource: "audit_logs"
    format: "excel"
    schedule: "0 3 * * 1"  # 3 AM every Monday
    retention_days: 90
```

## Segurança da API

### Melhores Práticas

1. **Use HTTPS sempre**: Nunca envie dados sensíveis via HTTP
2. **Rotação de Tokens**: Renove tokens regularmente
3. **Validação de Input**: Sempre valide dados de entrada
4. **Logging Sensível**: Não registre tokens ou senhas em logs
5. **IP Whitelisting**: Restrinja acesso a IPs conhecidos quando possível

### Headers de Segurança

A API inclui automaticamente headers de segurança:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## Monitoramento e Métricas

### Endpoints de Saúde

#### GET `/api/v1/health`
Verifica saúde da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-14T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "plugins": "loaded: 5"
  },
  "metrics": {
    "uptime": "7d 3h 15m",
    "memory_usage": "45%",
    "active_sessions": 42
  }
}
```

#### GET `/api/v1/metrics`
Retorna métricas do sistema em formato Prometheus.

### Logs de API

Todos os requests à API são registrados:

```json
{
  "timestamp": "2026-04-14T10:30:00Z",
  "method": "POST",
  "endpoint": "/api/v1/transactions/DS_QUERY/execute",
  "user_id": 123,
  "ip_address": "192.168.1.100",
  "user_agent": "Python/3.9",
  "response_time": 0.125,
  "status_code": 200
}
```

## Exemplos de Uso

### Script de Automação Python

```python
import asyncio
from devstation_sdk import DevStationClient

async def daily_report():
    client = DevStationClient(
        base_url="https://devstation.example.com",
        api_key="sua_chave_api"
    )
    
    # Autenticar
    await client.auth.login("automation", "senha_segura")
    
    # Executar relatório diário
    result = await client.transactions.execute(
        code="DS_DAILY_REPORT",
        parameters={
            "date": "2026-04-14",
            "format": "pdf"
        }
    )
    
    # Enviar por email
    await client.integrations.call_api(
        api_name="email_service",
        endpoint="/send",
        method="POST",
        data={
            "to": "management@company.com",
            "subject": "Relatório Diário",
            "attachment": result["report_data"]
        }
    )
    
    print("Relatório enviado com sucesso")

asyncio.run(daily_report())
```

### Integração com Power BI

```python
# Script para exportar dados para Power BI
import pandas as pd
from devstation_sdk import DevStationClient

client = DevStationClient("https://devstation.example.com", "api_key")

# Obter dados de transações
transactions = client.transactions.get_logs(
    start_date="2026-04-01",
    end_date="2026-04-14"
)

# Converter para DataFrame
df = pd.DataFrame(transactions["data"])

# Salvar para Power BI
df.to_csv("transactions_data.csv", index=False)
print(f"Exportados {len(df)} registros")
```

## Troubleshooting

### Erros Comuns

#### 401 Unauthorized
- Token expirado ou inválido
- Refresh token necessário
- Credenciais incorretas

#### 403 Forbidden
- Usuário não tem permissão para a ação
- IP bloqueado ou não autorizado
- Limite de rate atingido

#### 422 Unprocessable Entity
- Parâmetros inválidos ou faltando
- Validação de negócio falhou
- Dados em formato incorreto

### Debugging

Ative logging detalhado:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
client = DevStationClient(..., debug=True)
```

### Suporte

Para problemas com a API:
1. Verifique documentação em `/api/v1/docs`
2. Consulte logs em `/api/v1/admin/logs` (se autorizado)
3. Contate suporte: api-support@devstation.com

---

**API Version**: 1.0.