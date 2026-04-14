# Guia Arquitetural DevStationPlatform

## Visão Geral da Plataforma

DevStationPlatform é uma plataforma RAD (Rapid Application Development) inspirada em SAP com rastreabilidade total. A arquitetura segue princípios de separação de responsabilidades, extensibilidade e auditoria completa.

### Princípios Fundamentais

1. **Rastreabilidade Total**: Todas as ações são registradas em logs de auditoria
2. **RBAC Avançado**: Controle de acesso baseado em perfis dinâmicos
3. **Arquitetura Plugin**: Sistema extensível via plugins
4. **Separação Core/UI**: Backend independente da interface
5. **Transações como Unidade**: Tudo é uma transação auditável

## Arquitetura em Camadas

```
┌─────────────────────────────────────────────────┐
│                    INTERFACE                     │
│  (NiceGUI - Páginas e Componentes Visuais)      │
├─────────────────────────────────────────────────┤
│                    APLICAÇÃO                     │
│  (Rotas, Autenticação, Middleware, Serviços)    │
├─────────────────────────────────────────────────┤
│                      CORE                        │
│  (Config, Segurança, Plugins, Transações, KPI)  │
├─────────────────────────────────────────────────┤
│                     MODELOS                      │
│  (ORM, Entidades de Domínio, Validações)        │
├─────────────────────────────────────────────────┤
│                    INFRAESTRUTURA                │
│  (Banco de Dados, Logs, Configuração Externa)   │
└─────────────────────────────────────────────────┘
```

## 1. Camada de Infraestrutura

### 1.1 Configuração Centralizada
- **Classe Principal**: `Config` (singleton)
- **Localização**: `core/config.py`
- **Formato**: YAML (`config.yaml`)
- **Propósito**: Gerenciamento unificado de configurações

**Características**:
- Suporte a notação por pontos (`app.debug`, `database.dialect`)
- Valores padrão quando configuração ausente
- Configuração específica por ambiente (dev/staging/prod)

### 1.2 Banco de Dados
- **ORM**: SQLAlchemy
- **Dialetos Suportados**: SQLite (padrão), PostgreSQL, MySQL
- **Modelos Base**: `core/models/base.py`
- **Migrações**: Alembic (planejado)

**Estrutura de Modelos**:
```
core/models/
├── base.py          # BaseModel com métodos comuns
├── user.py          # Usuários e perfis
├── audit.py         # Logs de auditoria
└── __init__.py      # Exportação de modelos
```

## 2. Camada de Modelos (Domínio)

### 2.1 Entidades Principais

#### User (Usuário)
- **Arquivo**: `core/models/user.py`
- **Atributos**: id, username, email, full_name, is_active
- **Relacionamentos**: Perfis (many-to-many)
- **Métodos**: `to_dict()`, `has_profile()`, `has_permission()`

#### Profile (Perfil de Acesso)
- **Arquivo**: `core/security/models.py`
- **Hierarquia**: Herança entre perfis (ex: DEVELOPER → BANALYST → PUSER → USER)
- **Prioridade**: Define precedência (1-100)
- **Sistema**: Perfis padrão não podem ser excluídos

#### Permission (Permissão)
- **Categorias**: TRANSACTION, PLUGIN, DATA, ADMIN, IA
- **Granularidade**: Código único (ex: `transaction.execute`)
- **Associação**: Perfis possuem múltiplas permissões

#### AuditLog (Auditoria)
- **Arquivo**: `core/models/audit.py`
- **Campos**: timestamp, user_id, transaction_code, action_type, object_type, object_name
- **KPI Tags**: Marcadores para métricas (ex: `["auth", "login"]`)

## 3. Camada Core (Núcleo da Plataforma)

### 3.1 Sistema de Segurança (RBAC)
- **Módulo**: `core/security/`
- **Componentes**:
  - `auth.py`: Autenticação JWT
  - `rbac.py`: Controle de acesso baseado em papéis
  - `profile_manager.py`: Gerenciamento de perfis dinâmicos
  - `dynamic_profiles.py`: Perfis com herança

**Fluxo de Autenticação**:
```
1. Login → AuthService.authenticate()
2. Validação → RBAC.authenticate()
3. Token JWT → Armazenado em sessão
4. Middleware → Verifica cada requisição
5. Logout → Invalida token e limpa sessão
```

### 3.2 Gerenciador de Plugins
- **Classe**: `PluginManager`
- **Arquivo**: `core/plugin_manager.py`
- **Recursos**:
  - Auto-descoberta em diretório `plugins/`
  - Ativação/desativação dinâmica
  - Hooks para eventos do sistema
  - Isolamento de execução

**Estrutura de Plugin**:
```python
# Exemplo mínimo
class MeuPlugin:
    name = "Meu Plugin"
    version = "1.0.0"
    
    def register(self, plugin_manager):
        # Registrar rotas, comandos, etc.
        pass
```

### 3.3 Sistema de Transações
- **Classe**: `Transaction`
- **Decorador**: `@transaction`
- **Arquivo**: `core/transaction.py`
- **Propósito**: Unidade básica de trabalho auditável

**Características das Transações**:
- Código único (ex: `DS_QUERY`, `DS_USERS`)
- Rastreamento automático no audit log
- Coleta de métricas (KPI)
- Validação de permissões
- Rollback automático em erros

### 3.4 Coletor de KPI (Métricas)
- **Classe**: `KPICollector`
- **Arquivo**: `core/kpi/collector.py`
- **Métricas**:
  - Tempo de execução de transações
  - Taxa de sucesso/erro
  - Uso por perfil de usuário
  - Frequência de ações

### 3.5 Logger de Auditoria
- **Classe**: `AuditLogger`
- **Arquivo**: `core/audit_logger.py`
- **Logs**: Arquivo dedicado (`logs/audit.log`)
- **Estrutura**: JSON com todos os campos relevantes
- **Integração**: Automática com transações

## 4. Camada de Aplicação

### 4.1 App Principal (NiceGUI)
- **Arquivo**: `ui/app.py`
- **Função**: `create_app()`
- **Responsabilidades**:
  - Configuração de rotas
  - Middleware de autenticação
  - Tema global (CSS compartilhado)
  - Gerenciamento de sessão

### 4.2 Sistema de Rotas
- **Mapeamento**: Decoradores `@ui.page()`
- **Proteção**: Middleware verifica autenticação
- **Redirecionamento**: `/` → login ou dashboard
- **Rotas Principais**:
  - `/login` - Autenticação
  - `/dashboard` - Dashboard principal
  - `/admin/*` - Administração
  - `/tools/*` - Ferramentas de desenvolvimento
  - `/profile` - Perfil do usuário
  - `/settings` - Configurações

### 4.3 Serviço de Autenticação
- **Classe**: `AuthService` (em `ui/app.py`)
- **Métodos**:
  - `authenticate()`: Valida credenciais
  - `validate_token()`: Verifica sessão ativa
  - `logout()`: Encerra sessão
- **Integração**: Com RBAC do core

### 4.4 Gerenciamento de Sessão
- **Storage**: `app.storage.user`
- **Estrutura**:
```python
{
    'authenticated': True/False,
    'user_data': {id, username, profiles, ...},
    'token': 'jwt_token_string'
}
```
- **Persistência**: Entre recarregamentos de página
- **Timeout**: Configurável (padrão: 30 minutos)

## 5. Camada de Interface (UI)

### 5.1 Estrutura de Páginas
```
ui/pages/
├── login.py              # Tela de autenticação
├── dashboard.py          # Dashboard principal
├── admin_users.py        # Gestão de usuários
├── admin_profiles.py     # Gestão de perfis
├── admin_audit.py        # Visualização de logs
├── tools_query.py        # Console SQL (DS_QUERY)
├── tools_table.py        # Navegador de tabelas
├── designer.py           # UI Designer
├── user_profile.py       # Perfil do usuário
├── user_settings.py      # Configurações
└── tools_plugins.py      # Gerenciador de plugins
```

### 5.2 Componentes Visuais
```
views/components/
├── badges.py     # Badges de status
├── cards.py      # Cards com informações
├── controls.py   # Controles customizados
├── style.py      # Estilos CSS
├── tx_bar.py     # Barra de transações
└── __init__.py   # Exportação de componentes
```

### 5.3 Views (Telas Complexas)
```
views/
├── dashboard.py      # Dashboard principal
├── ds_audit.py       # Tela de auditoria
├── ds_chg.py         # Tela de mudanças
├── ds_kpi_dash.py    # Dashboard de KPI
└── ds_users.py       # Tela de usuários
```

### 5.4 Sistema de Temas
- **CSS Global**: Definido em `ui/app.py`
- **Variáveis CSS**: Cores, espaçamentos, tipografia
- **Modo Escuro**: Forçado para toda aplicação
- **Componentes Quasar**: Personalizados com classes `.ds-*`

## 6. Fluxos de Trabalho Principais

### 6.1 Fluxo de Autenticação
```
1. Usuário acessa `/` → redireciona para `/login`
2. Submete credenciais → AuthService.authenticate()
3. RBAC valida → retorna dados do usuário + token
4. Sessão é criada → app.storage.user atualizado
5. Audit log registra login → KPI coletado
6. Redireciona para `/dashboard`
```

### 6.2 Fluxo de Transação
```
1. Usuário executa ação (ex: consulta SQL)
2. Decorador @transaction intercepta
3. Verifica permissões do usuário
4. Inicia timer para KPI
5. Executa função principal
6. Registra no audit log (sucesso/erro)
7. Coleta métricas (tempo, resultado)
8. Retorna resultado para usuário
```

### 6.3 Fluxo de Administração
```
1. Usuário com perfil ADMIN acessa `/admin/users`
2. Middleware valida permissão `admin.users`
3. Página carrega lista de usuários do banco
4. Ações (criar/editar/excluir) são transações
5. Cada ação gera entrada no audit log
6. KPI coleta métricas de uso administrativo
```

## 7. Sistema de Permissões

### 7.1 Hierarquia de Perfis
```
ADMIN (100)
└── DEV_ALL (60)
    └── CORE_DEV (50)
        └── DEVELOPER (40)
            └── BANALYST (30)
                └── PUSER (20)
                    └── USER (10)
```

**Regras**:
- Perfis herdam permissões dos pais
- Prioridade define precedência em conflitos
- Perfis do sistema não podem ser excluídos
- Perfis customizados podem ser criados

### 7.2 Categorias de Permissão
1. **TRANSACTION**: Execução/criação/modificação de transações
2. **PLUGIN**: Instalação/desenvolvimento/publicação de plugins
3. **DATA**: Consulta/exportação/importação de dados
4. **ADMIN**: Gestão de usuários, perfis, permissões, auditoria
5. **IA**: Consulta e treinamento de modelos de IA

### 7.3 Verificação de Permissões
```python
# No código
@requires_permission("transaction.execute")
def execute_query():
    pass

# No middleware
if not user.has_permission("admin.users"):
    return redirect("/dashboard")
```

## 8. Sistema de Plugins

### 8.1 Arquitetura de Plugin
```
plugins/
├── meu_plugin/
│   ├── __init__.py      # Classe principal do plugin
│   ├── routes.py        # Rotas adicionais
│   ├── components.py    # Componentes visuais
│   └── manifest.yaml    # Metadados do plugin
└── __init__.py          # Registro automático
```

### 8.2 Ciclo de Vida do Plugin
1. **Descoberta**: PluginManager varre diretório `plugins/`
2. **Carregamento**: Importa classe principal do plugin
3. **Registro**: Plugin se registra no manager
4. **Ativação**: Hooks são conectados ao sistema
5. **Execução**: Plugin responde a eventos
6. **Desativação**: Hooks são desconectados

### 8.3 Hooks Disponíveis
- `on_app_start`: Quando aplicação inicia
- `on_user_login`: Após login de usuário
- `on_transaction_execute`: Antes/depois de transação
- `on_menu_render`: Durante construção do menu
- `on_audit_log`: Quando log de auditoria é criado

## 9. Sistema de Menu

### 9.1 Configuração do Menu
- **Arquivo**: `config.yaml` (seção `menu.structure`)
- **Gerenciador**: `MenuManager` (`core/menu_manager.py`)
- **Renderização**: Dinâmica baseada em permissões

### 9.2 Estrutura do Menu
```yaml
menu:
  structure:
    - label: "Dashboard"
      icon: "dashboard"
      path: "/dashboard"
      permissions: ["transaction.execute"]
      
    - label: "Desenvolvimento"
      icon: "code"
      children:
        - label: "Query Console"
          path: "/tools/query"
          transaction: "DS_QUERY"
          permissions: ["transaction.execute"]
```

### 9.3 Filtragem por Permissão
- Itens sem `permissions` são sempre visíveis
- Itens com `permissions` exigem pelo menos uma permissão
- Submenus são ocultados se todos os filhos forem ocultados
- Menu é recalculado a cada mudança de perfil

## 10. Rastreabilidade e Auditoria

### 10.1 O Que É Rastreado
1. **Autenticação**: Logins/logouts, tentativas falhas
2. **Transações**: Execução, parâmetros, resultado, duração
3. **Dados**: Criação, modificação, exclusão de registros
4. **Configuração**: Mudanças em perfis, permissões, usuários
5. **Sistema**: Inicialização, erros, eventos críticos

### 10.2 Estrutura do Log de Auditoria
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 123,
  "user_name": "joao.silva",
  "user_profiles": "DEVELOPER, BANALYST",
  "transaction_code": "DS_QUERY",
  "action_type": "EXECUTE",
  "object_type": "QUERY",
  "object_name": "SELECT * FROM users",
  "details": {"rows_affected": 42, "duration_ms": 150},
  "kpi_tags": ["query", "success"]
}
```

### 10.3 KPIs Coletados
- **Tempo de Resposta**: Por transação, por usuário
- **Taxa de Sucesso**: Sucesso vs erro por transação
- **Uso por Perfil**: Quais perfis usam quais funcionalidades
- **Frequência**: Horários de pico, padrões de uso
- **Performance**: Tempos de carregamento, uso de recursos

## 11. Convenções e Padrões

### 11.1 Convenções de Nomenclatura

#### Transações
- `DS_` prefixo para transações do sistema
- `NDS_` prefixo para transações customizadas
- Exemplos: `DS_QUERY`, `DS_USERS`, `NDS_CUSTOM_REPORT`

#### Permissões
- Formato: `categoria.acao.[subacao]`
- Exemplos: `transaction.execute`, `admin.users.create`, `data.export.csv`

#### Arquivos e Diretórios
- **Core**: `core/nome_do_modulo.py`
- **UI Pages**: `ui/pages/nome_da_p