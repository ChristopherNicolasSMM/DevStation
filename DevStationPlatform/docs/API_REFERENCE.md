# Referência de API DevStationPlatform

## Índice
1. [Core API](#core-api)
2. [Security API](#security-api)
3. [Transaction API](#transaction-api)
4. [Plugin API](#plugin-api)
5. [UI Utilities](#ui-utilities)
6. [Models Reference](#models-reference)

## 1. Core API

### Config (core/config.py)
Classe singleton para gerenciamento de configuração.

```python
from core.config import config

# Obter valor
debug = config.get("app.debug")
database_url = config.database_url

# Definir valor
config.set("app.debug", True)

# Propriedades
app_name = config.app_name
is_debug = config.debug
```

**Métodos**:
- `get(key, default=None)`: Obter valor por notação de pontos
- `set(key, value)`: Definir valor por notação de pontos
- `_load_config()`: Carregar configuração do YAML (interno)

**Propriedades**:
- `debug`: Modo de depuração (bool)
- `app_name`: Nome da aplicação (str)
- `database_url`: URL de conexão com banco (str)

### AuditLogger (core/audit_logger.py)
Sistema centralizado de logs de auditoria.

```python
from core.audit_logger import audit_logger

# Log básico
audit_logger.log(
    user_id=123,
    user_name="joao.silva",
    transaction_code="DS_QUERY",
    action_type="EXECUTE",
    object_type="QUERY",
    object_name="SELECT * FROM users",
    kpi_tags=["query", "success"]
)

# Log com detalhes extras
audit_logger.log_with_details(
    user_id=123,
    transaction_code="DS_EXPORT",
    details={"format": "CSV", "rows": 1000},
    kpi_tags=["export", "large"]
)
```

**Métodos**:
- `log(user_id, user_name, transaction_code, action_type, object_type, object_name, user_profiles="", details=None, kpi_tags=None)`: Log principal
- `log_with_details(user_id, transaction_code, details, kpi_tags=None)`: Log simplificado
- `get_recent_logs(limit=100)`: Obter logs recentes
- `search_logs(criteria)`: Buscar logs por critérios

### KPICollector (core/kpi/collector.py)
Coletor de métricas e indicadores de performance.

```python
from core.kpi.collector import kpi_collector

# Registrar transação
kpi_collector.record_transaction(
    code="DS_QUERY",
    duration_ms=150,
    success=True,
    user_id=123
)

# Obter métricas
metrics = kpi_collector.get_metrics(
    transaction_code="DS_QUERY",
    time_range="last_24_hours"
)

# Dashboard KPI
dashboard = kpi_collector.get_dashboard()
```

**Métodos**:
- `record_transaction(code, duration_ms, success, user_id=None)`: Registrar execução
- `get_metrics(transaction_code=None, time_range="last_hour")`: Obter métricas
- `get_dashboard()`: Dashboard completo
- `clear_old_data(days=30)`: Limpar dados antigos

## 2. Security API

### RBAC (core/security/rbac.py)
Controle de acesso baseado em papéis.

```python
from core.security.rbac import rbac

# Autenticação
result = rbac.authenticate(username, password)
if result:
    user_data = result["user"]
    token = result["token"]

# Validação de token
user = rbac.validate_token(token)

# Verificação de permissão
has_perm = rbac.has_permission(user_id, "transaction.execute")

# Logout
rbac.logout(token)
```

**Métodos**:
- `authenticate(username, password)`: Autenticar usuário
- `validate_token(token)`: Validar token JWT
- `has_permission(user_or_id, permission_code)`: Verificar permissão
- `logout(token)`: Invalidar token
- `get_user_profiles(user_id)`: Obter perfis do usuário

### ProfileManager (core/security/profile_manager.py)
Gerenciamento de perfis dinâmicos.

```python
from core.security.profile_manager import profile_manager

# Obter perfil
profile = profile_manager.get_profile("DEVELOPER")

# Verificar herança
is_child = profile_manager.is_child_of("DEVELOPER", "USER")

# Obter todas as permissões
permissions = profile_manager.get_all_permissions("DEVELOPER")

# Criar perfil customizado
new_profile = profile_manager.create_profile(
    code="CUSTOM",
    name="Perfil Customizado",
    inherit_from=["USER", "PUSER"]
)
```

**Métodos**:
- `get_profile(profile_code)`: Obter perfil por código
- `get_all_profiles()`: Listar todos os perfis
- `create_profile(code, name, description="", inherit_from=None, is_system=False, priority=0)`: Criar novo perfil
- `update_profile(profile_code, **updates)`: Atualizar perfil
- `delete_profile(profile_code)`: Excluir perfil (não sistema)
- `is_child_of(child_code, parent_code)`: Verificar herança
- `get_all_permissions(profile_code)`: Todas as permissões (com herança)

### AuthService (ui/app.py)
Serviço de autenticação para UI.

```python
from ui.app import AuthService

# Autenticar
user_data = AuthService.authenticate(username, password)

# Validar sessão
current_user = AuthService.validate_token(token)

# Logout
AuthService.logout(token)
```

**Métodos Estáticos**:
- `authenticate(username, password)`: Autenticar e retornar dados do usuário
- `validate_token(token)`: Validar token e retornar usuário
- `logout(token)`: Invalidar token

## 3. Transaction API

### Decorator @transaction
Decorador para criar transações auditáveis.

```python
from core.transaction import transaction

@transaction("DS_MINHA_TRANSACAO")
def minha_transacao(param1, param2, user_id=None):
    """
    Transação de exemplo.
    
    Args:
        param1: Primeiro parâmetro
        param2: Segundo parâmetro
        user_id: ID do usuário (automático)
    
    Returns:
        Resultado da transação
    """
    # Lógica da transação
    resultado = processar(param1, param2)
    
    # Retorno automático para audit log
    return resultado
```

**Parâmetros Automáticos**:
- `user_id`: ID do usuário atual (se autenticado)
- `transaction_id`: ID único da execução
- `start_time`: Timestamp de início

**Comportamento**:
1. Valida permissões do usuário
2. Inicia timer para KPI
3. Executa função
4. Registra no audit log (sucesso/erro)
5. Coleta métricas
6. Retorna resultado

### Classe Transaction
Context manager para transações complexas.

```python
from core.transaction import Transaction

def transacao_complexa():
    with Transaction("DS_TRANSACAO_COMPLEXA", user_id=123) as tx:
        # Passo 1
        resultado1 = passo1()
        tx.add_context("passo1_result", resultado1)
        
        # Passo 2 (depende do 1)
        resultado2 = passo2(resultado1)
        
        # Commit implícito no final do bloco
        return resultado2
    
    # Rollback automático em caso de exceção
```

**Métodos**:
- `add_context(key, value)`: Adicionar contexto ao log
- `set_result(result)`: Definir resultado manualmente
- `add_kpi_tag(tag)`: Adicionar tag KPI

**Propriedades**:
- `transaction_id`: ID único
- `user_id`: ID do usuário
- `start_time`: Início da transação
- `duration_ms`: Duração (após conclusão)

## 4. Plugin API

### PluginManager (core/plugin_manager.py)
Gerenciamento central de plugins.

```python
from core.plugin_manager import plugin_manager

# Carregar plugins
plugin_manager.load_plugins()

# Listar plugins
plugins = plugin_manager.list_plugins()

# Ativar/desativar
plugin_manager.enable_plugin("meu_plugin")
plugin_manager.disable_plugin("meu_plugin")

# Executar hook
plugin_manager.execute_hook("on_user_login", user_data)
```

**Métodos**:
- `load_plugins()`: Carregar todos os plugins
- `list_plugins()`: Listar plugins disponíveis
- `get_plugin(name)`: Obter plugin específico
- `enable_plugin(name)`: Ativar plugin
- `disable_plugin(name)`: Desativar plugin
- `register_hook(hook_name, callback)`: Registrar hook (para plugins)
- `execute_hook(hook_name, *args, **kwargs)`: Executar hook
- `add_menu_item(item)`: Adicionar item ao menu (para plugins)

**Hooks Disponíveis**:
- `on_app_start`: Quando aplicação inicia
- `on_app_shutdown`: Quando aplicação termina
- `on_user_login(user_data)`: Após login de usuário
- `on_user_logout(user_data)`: Após logout de usuário
- `on_transaction_execute(transaction_code, user_id, params, result)`: Após execução de transação
- `on_audit_log(log_entry)`: Quando log de auditoria é criado
- `on_menu_render(menu_items)`: Durante renderização do menu

### Base Plugin Class
Classe base para desenvolvimento de plugins.

```python
from core.plugin_manager import BasePlugin

class MeuPlugin(BasePlugin):
    """Plugin de exemplo"""
    
    name = "Meu Plugin"
    version = "1.0.0"
    author = "Seu Nome"
    
    def register(self):
        """Chamado durante registro"""
        self.logger.info(f"{self.name} registrado")
        
    def enable(self):
        """Chamado durante ativação"""
        # Registrar hooks
        self.register_hook("on_user_login", self.handle_login)
        
        # Adicionar rotas
        self.add_route("/meu-plugin", self.render_page)
        
    def disable(self):
        """Chamado durante desativação"""
        # Limpar recursos
        
    def handle_login(self, user_data):
        """Handler para hook"""
        self.logger.info(f"Usuário {user_data['username']} logou")
```

**Métodos da Classe Base**:
- `register()`: Chamado durante registro
- `enable()`: Chamado durante ativação
- `disable()`: Chamado durante desativação
- `register_hook(hook_name, callback)`: Registrar hook
- `add_route(path, handler)`: Adicionar rota
- `add_menu_item(item)`: Adicionar item ao menu
- `get_config(key, default=None)`: Obter configuração
- `set_config(key, value)`: Definir configuração

## 5. UI Utilities

### Authentication Utilities (ui/app.py)
Utilitários para autenticação na UI.

```python
from ui.app import login_user, logout_user, get_current_user, requires_permission

# Login
login_user(user_data, token)

# Logout
logout_user()

# Obter usuário atual
user = get_current_user()

# Decorador de permissão
@requires_permission("transaction.execute")
def pagina_protegida():
    ui.label("Página protegida")
```

**Funções**:
- `login_user(user_data, token)`: Realizar login
- `logout_user()`: Realizar logout
- `get_current_user()`: Obter usuário atual
- `requires_permission(permission_code)`: Decorador para verificação

### Menu System
Sistema de menu dinâmico baseado em permissões.

```python
from core.menu_manager import menu_manager

# Obter menu para usuário
menu_items = menu_manager.get_menu_for_user(user_id)

# Adicionar item dinamicamente (plugins)
menu_manager.add_item({
    "label": "Novo Item",
    "icon": "add",
    "path": "/novo",
    "permissions": ["novo.acessar"]
})
```

**Estrutura do Item de Menu**:
```python
{
    "label": "Texto exibido",
    "icon": "nome_icone",  # Opcional
    "path": "/caminho",    # Ou "children" para submenu
    "permissions": ["perm1", "perm2"],  # Opcional
    "transaction": "DS_CODIGO",  # Opcional
    "children": [  # Para submenus
        {"label": "Subitem", "path": "/subitem"}
    ]
}
```

### Theme System
Sistema de temas CSS global.

**Variáveis CSS Disponíveis**:
```css
:root {
    --ds-bg: #0e1117;           /* Background principal */
    --ds-surface: #161b22;      /* Superfícies (cards) */
    --ds-accent: #58a6ff;       /* Cor de destaque */
    --ds-text: #c9d1d9;         /* Texto principal */
    --ds-text-secondary: #8b949e; /* Texto secundário */
    --ds-border: #30363d;       /* Bordas */
    --ds-success: #238636;      /* Sucesso */
    --ds-warning: #d29922;      /* Aviso */
    --ds-error: #f85149;        /* Erro */
}
```

**Classes CSS**:
- `.ds-card`: Card com estilo padrão
- `.ds-btn-primary`: Botão primário
- `.ds-btn-secondary`: Botão secundário
- `.ds-sidebar`: Sidebar
- `.ds-header`: Cabeçalho
- `.ds-table`: Tabela estilizada

## 6. Models Reference

### BaseModel (core/models/base.py)
Classe base para todos os modelos.

```python
from core.models.base import BaseModel

class MeuModelo(BaseModel):
    __tablename__ = "meu_modelo"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100))
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome
        }
```

**Métodos Herdados**:
- `to_dict()`: Converter para dicionário
- `save()`: Salvar no banco
- `delete()`: Excluir do banco
- `update(**kwargs)`: Atualizar campos

**Propriedades**:
- `created_at`: Data de criação (automático)
- `updated_at`: Data de atualização (automático)

### User Model (core/models/user.py)
Modelo de usuário do sistema.

```python
from core.models.user import User

# Criar usuário
user = User.create(
    username="novo.usuario",
    email="usuario@email.com",
    full_name="Novo Usuário",
    password_hash="hash_da_senha"
)

# Buscar usuário
user = User.get_by_username("joao.silva")

# Verificar senha
is_valid = user.check_password("senha123")

# Obter perfis
profiles = user.get_profiles()

# Verificar permissão
has_perm = user.has_permission("transaction.execute")
```

**Métodos Estáticos**:
- `create(**kwargs)`: Criar novo usuário
- `get_by_username(username)`: Buscar por username
- `get_by_email(email)`: Buscar por email
- `get_by_id(user_id)`: Buscar por ID

**Métodos de Instância**:
- `check_password(password)`: Verificar senha
- `set_password(password)`: Definir nova senha
- `get_profiles()`: Obter perfis do usuário
- `has_profile(profile_code)`: Verificar se tem perfil
- `has_permission(permission_code)`: Verificar permissão
- `add_profile(profile_code)`: Adicionar perfil
- `remove_profile(profile_code)`: Remover perfil

### AuditLog Model (core/models/audit.py)
Modelo de log de auditoria.

```python
from core.models.audit import AuditLog

# Criar log manualmente
log = AuditLog.create(
    user_id=123,
    user_name="joao.silva",
    transaction_code="DS_CUSTOM",
    action_type="CREATE",
    object_type="DOCUMENT",
    object_name="Relatório Mensal"
)

# Buscar logs
logs = AuditLog.get_by_user(123, limit=50)
logs = AuditLog.get_by_transaction("DS_QUERY", limit=100)
logs = AuditLog.search(
    start_date="2024-01-01",
    end_date="2024-01-31",
    action_type="EXECUTE"
)
```

**Métodos Estáticos**:
- `create(**kwargs)`: Criar novo log
- `get_by_user(user_id, limit=100)`: Buscar por usuário
- `get_by_transaction(transaction_code, limit=100)`: Buscar por transação
- `search(**filters)`: Busca avançada com filtros
- `get_recent(limit=100)`: Logs mais recentes

**Campos**:
- `id`: ID único
- `timestamp`: Data/hora do evento
- `user_id`: ID do usuário
- `user_name`: Nome do usuário
- `