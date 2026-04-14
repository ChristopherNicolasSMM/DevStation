# Arquitetura do Core do Sistema

## Visão Geral do Core

O **Core** do DevStationPlatform é o coração do sistema, contendo toda a lógica de negócio, segurança, gerenciamento de transações e infraestrutura. Este documento descreve a arquitetura interna do módulo `core/`.

## Estrutura do Módulo Core

```
core/
├── 📄 __init__.py              # Inicialização e exports
├── 📄 config.py               # Gerenciador de configuração
├── 📄 transaction.py          # Sistema de transações
├── 📄 plugin_manager.py       # Gerenciador de plugins
├── 📄 menu_manager.py         # Gerenciador de menus dinâmicos
├── 📄 audit_logger.py         # Sistema de auditoria
├── 📄 theme.py                # Gerenciador de temas
│
├── 📁 models/                 # Modelos de dados
│   ├── 📄 __init__.py
│   ├── 📄 base.py            # Modelo base SQLAlchemy
│   ├── 📄 user.py            # Modelo de usuário
│   ├── 📄 audit.py           # Modelo de auditoria
│   └── 📄 ... outros
│
├── 📁 security/               # Sistema de segurança
│   ├── 📄 __init__.py
│   ├── 📄 auth.py            # Autenticação JWT
│   ├── 📄 rbac.py            # Controle de acesso RBAC
│   ├── 📄 models.py          # Modelos de segurança
│   ├── 📄 profile_manager.py # Gerenciador de perfis
│   └── 📄 dynamic_profiles.py # Perfis dinâmicos
│
└── 📁 kpi/                    # Métricas e KPIs
    ├── 📄 __init__.py
    └── 📄 collector.py       # Coletor de métricas
```

## Componentes Principais

### 1. Gerenciador de Configuração (`config.py`)

#### Responsabilidades:
- Carregar configurações do arquivo `config.yaml`
- Gerenciar variáveis de ambiente
- Fornecer acesso unificado às configurações
- Validar configurações obrigatórias

#### Interface Principal:
```python
class Config:
    def __init__(self, config_path="config.yaml"):
        self.settings = self._load_config(config_path)
        self._override_with_env_vars()
    
    def get(self, key: str, default=None):
        """Obtém valor de configuração"""
        pass
    
    def set(self, key: str, value):
        """Define valor de configuração"""
        pass
    
    def reload(self):
        """Recarrega configurações"""
        pass
```

#### Fluxo de Carregamento:
```
1. Carrega config.yaml → dict
2. Sobrescrede com variáveis de ambiente
3. Valida estrutura obrigatória
4. Disponibiliza via singleton
```

### 2. Sistema de Transações (`transaction.py`)

#### Conceito de Transação:
No DevStationPlatform, uma **transação** é uma unidade de trabalho que:
- Tem código único (ex: `DS_QUERY`, `DS_USERS`)
- Define parâmetros de entrada
- Implementa lógica de negócio específica
- Registra auditoria automática
- Pode requerer aprovação

#### Componentes:

```python
class Transaction:
    """Classe base para todas as transações"""
    code: str
    name: str
    description: str
    parameters_schema: dict
    
    def execute(self, user: User, parameters: dict) -> dict:
        """Executa a transação"""
        pass
    
    def validate_parameters(self, parameters: dict) -> bool:
        """Valida parâmetros de entrada"""
        pass

class TransactionFactory:
    """Factory para criação de transações"""
    def create_transaction(self, code: str) -> Transaction:
        pass
    
    def register_transaction(self, code: str, transaction_class):
        pass

class TransactionExecutor:
    """Orquestra execução de transações"""
    def execute(self, transaction_code: str, user: User, params: dict) -> dict:
        pass
```

#### Fluxo de Execução:
```
1. Validação de acesso do usuário
2. Validação de parâmetros
3. Execução da lógica de negócio
4. Persistência de resultados
5. Registro de auditoria
6. Retorno de resposta
```

### 3. Gerenciador de Plugins (`plugin_manager.py`)

#### Arquitetura de Plugins:
- **Hot-reload**: Recarregamento automático em desenvolvimento
- **Isolamento**: Plugins não interferem no core
- **Dependências**: Cada plugin gerencia suas próprias dependências
- **Hooks**: Sistema de hooks para extensão

#### Componentes:

```python
class BasePlugin:
    """Classe base para todos os plugins"""
    name: str
    version: str
    description: str
    
    def initialize(self, config: Config):
        """Inicialização do plugin"""
        pass
    
    def register_routes(self, app):
        """Registro de rotas/views"""
        pass

class PluginManager:
    """Gerencia ciclo de vida dos plugins"""
    def load_plugin(self, plugin_path: str) -> BasePlugin:
        pass
    
    def unload_plugin(self, plugin_name: str):
        pass
    
    def get_plugin(self, plugin_name: str) -> BasePlugin:
        pass
```

#### Fluxo de Carregamento:
```
1. Descoberta de plugins no diretório plugins/
2. Validação de estrutura do plugin
3. Carregamento dinâmico do módulo
4. Inicialização do plugin
5. Registro de hooks e rotas
```

### 4. Sistema de Segurança (`security/`)

#### Módulos de Segurança:

##### Autenticação (`auth.py`):
- JWT (JSON Web Tokens) com expiração
- BCrypt para hash de senhas
- Refresh tokens
- Bloqueio após tentativas falhas

```python
class AuthService:
    def authenticate(self, username: str, password: str) -> dict:
        """Autentica usuário e retorna token"""
        pass
    
    def validate_token(self, token: str) -> dict:
        """Valida token JWT"""
        pass
    
    def logout(self, token: str):
        """Invalida token"""
        pass
```

##### RBAC (`rbac.py`):
- Controle de acesso baseado em papéis
- Perfis dinâmicos com herança
- Permissões granulares
- Cache de permissões para performance

```python
class RBACManager:
    def check_permission(self, user: User, permission_code: str) -> bool:
        """Verifica se usuário tem permissão"""
        pass
    
    def get_user_permissions(self, user: User) -> list:
        """Obtém todas as permissões do usuário"""
        pass
```

##### Perfis Dinâmicos (`dynamic_profiles.py`):
- Criação dinâmica de perfis
- Herança entre perfis
- Prioridade de perfis
- Perfis do sistema vs. customizados

### 5. Sistema de Auditoria (`audit_logger.py`)

#### O que é Auditado:
- Todas as transações executadas
- Logins e tentativas de acesso
- Alterações em dados sensíveis
- Mudanças de configuração
- Eventos de segurança

#### Componentes:

```python
class AuditLogger:
    def log_action(self, user: User, action: str, 
                   resource_type: str, resource_id: str,
                   old_values: dict, new_values: dict):
        """Registra ação de auditoria"""
        pass
    
    def log_transaction(self, transaction: Transaction, 
                        user: User, parameters: dict, 
                        result: dict, status: str):
        """Registra execução de transação"""
        pass
    
    def get_audit_trail(self, filters: dict) -> list:
        """Obtém logs de auditoria filtrados"""
        pass
```

#### Estrutura do Log:
```json
{
  "id": 123,
  "user_id": 456,
  "action": "USER_UPDATED",
  "resource_type": "User",
  "resource_id": "789",
  "old_values": {"name": "Antigo"},
  "new_values": {"name": "Novo"},
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 6. Gerenciador de Menus (`menu_manager.py`)

#### Menus Dinâmicos:
- Estrutura hierárquica
- Baseado em permissões do usuário
- Configurável via `config.yaml`
- Atualização em tempo real

```python
class MenuManager:
    def get_user_menu(self, user: User) -> list:
        """Obtém menu filtrado por permissões"""
        pass
    
    def add_menu_item(self, item: dict):
        """Adiciona item ao menu"""
        pass
    
    def reload_menu(self):
        """Recarrega menu da configuração"""
        pass
```

#### Estrutura do Menu:
```yaml
menu:
  structure:
    - label: "Dashboard"
      icon: "dashboard"
      path: "/dashboard"
      permissions: ["transaction.execute"]
    
    - label: "Administração"
      icon: "admin"
      permissions: ["admin.users"]
      children:
        - label: "Usuários"
          path: "/admin/users"
          transaction: "DS_USERS"
```

### 7. Modelos de Dados (`models/`)

#### Base Model (`base.py`):
```python
class BaseModel:
    """Modelo base SQLAlchemy com campos comuns"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte modelo para dict"""
        pass
```

#### User Model (`user.py`):
```python
class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profiles = relationship("Profile", secondary="user_profiles")
    
    def check_password(self, password: str) -> bool:
        """Verifica senha com BCrypt"""
        pass
```

### 8. Sistema de KPIs (`kpi/collector.py`)

#### Métricas Coletadas:
- Uso do sistema por usuário
- Performance de transações
- Erros e exceções
- Uso de recursos
- Comportamento do usuário

```python
class KPICollector:
    def collect_transaction_metrics(self, transaction_log: TransactionLog):
        """Coleta métricas de transação"""
        pass
    
    def collect_user_activity(self, user: User, action: str):
        """Coleta atividade do usuário"""
        pass
    
    def generate_report(self, start_date, end_date) -> dict:
        """Gera relatório de KPIs"""
        pass
```

## Padrões de Design no Core

### 1. Singleton Pattern
- **Config**: Única instância de configuração
- **Database Session**: Gerenciamento centralizado
- **Plugin Manager**: Controle único de plugins

### 2. Factory Pattern
- **TransactionFactory**: Cria transações dinamicamente
- **PluginFactory**: Instancia plugins

### 3. Strategy Pattern
- **Authentication Strategies**: JWT, OAuth, LDAP
- **Transaction Handlers**: Diferentes implementações

### 4. Observer Pattern
- **Audit System**: Observa eventos do sistema
- **Plugin Hooks**: Notifica plugins de eventos

### 5. Repository Pattern
- **Data Access**: Abstração do banco de dados
- **Caching Layer**: Cache de consultas frequentes

## Fluxos de Trabalho Principais

### Fluxo 1: Execução de Transação
```
1. Usuário solicita transação via UI
2. UI chama TransactionExecutor
3. Executor valida permissões (RBAC)
4. Executor cria transação via Factory
5. Transação valida parâmetros
6. Transação executa lógica de negócio
7. AuditLogger registra execução
8. KPICollector coleta métricas
9. Resultado retornado para UI
```

### Fluxo 2: Autenticação
```
1. Usuário envia credenciais
2. AuthService valida com BCrypt
3. RBACManager obtém permissões do usuário
4. AuthService gera token JWT com permissões
5. AuditLogger registra login
6. Token retornado para cliente
7. Cliente usa token em requests subsequentes
```

### Fluxo 3: Carregamento de Plugin
```
1. PluginManager descobre plugins
2. PluginLoader valida estrutura
3. PluginLoader instala dependências
4. PluginManager instancia plugin
5. Plugin inicializa e registra hooks
6. MenuManager atualiza menu com itens do plugin
7. Plugin disponível para uso
```

## Considerações de Performance

### 1. Cache Estratégico
```python
# Cache de permissões do usuário
@lru_cache(maxsize=1000)
def get_user_permissions(user_id: int) -> list:
    pass

# Cache de configurações
config_cache = TTLCache(maxsize=100, ttl=300)
```

### 2. Connection Pooling
```python
# SQLAlchemy com pool de conexões
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)
```

### 3. Lazy Loading
```python
# Carregamento preguiçoso de plugins
class PluginManager:
    def __init__(self):
        self._plugins = {}  # Plugins carregados sob demanda
    
    def get_plugin(self, name: str):
        if name not in self._plugins:
            self._load_plugin(name)
        return self._plugins[name]
```

## Testabilidade

### 1. Injeção de Dependências
```python
class TransactionExecutor:
    def __init__(self, audit_logger: AuditLogger, 
                 rbac_manager: RBACManager):
        self.audit_logger = audit_logger
        self.rbac_manager = rbac_manager
```

### 2. Interfaces Claramente Definidas
```python
class ITransaction(ABC):
    @abstractmethod
    def execute(self, user: User, parameters: dict) -> dict:
        pass
```

### 3. Mocks para Testes
```python
# Teste com mock
def test_transaction_execution():
    mock_audit = Mock(spec=AuditLogger)
    mock_rbac = Mock(spec=RBACManager)
    
    executor = TransactionExecutor(mock_audit, mock_rbac)
    # ... teste
```

## Extensibilidade

### 1. Hooks do Sistema
```python
# Plugin pode registrar hooks
plugin_manager.register_hook(
    "pre_transaction_execute",
    my_plugin.pre_execute_callback
)
```

### 2. Middleware Chain
```python
# Pipeline de processamento
middleware_chain = [
    AuthenticationMiddleware,
    AuthorizationMiddleware,
    AuditMiddleware,
    TransactionMiddleware
]
```

### 3. Event Bus
```python
# Sistema de eventos
event_bus.subscribe("user_created", send_welcome_email)
event_bus.subscribe("user_created", create_audit_log)
```

## Próximos Passos

1. [Explorar sistema de segurança](../03_core_sistema/02_seguranca_autenticacao.md)
2. [Entender gerenciamento de plugins](../03_core_sistema/03_gerenciamento_plugins.md)
3. [Ver sistema de transações](../03_core_sistema/04_sistema_transacoes.md)

---

**Core Version**: 1.0.0  
**Última Atualização**: 2026-04-14  
**Total de Classes**: ~25  
**Linhas de Código**: ~2,500  
**Test Coverage**: 88%