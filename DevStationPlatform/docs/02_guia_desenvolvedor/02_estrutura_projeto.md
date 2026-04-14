# Estrutura do Projeto

Este documento descreve a organização de arquivos e pastas do DevStationPlatform.

## Visão Geral da Estrutura

```
DevStationPlatform/
├── 📁 core/                    # Núcleo do sistema
├── 📁 ui/                      # Componentes de interface
├── 📁 views/                   # Views/páginas da aplicação
├── 📁 plugins/                 # Plugins do sistema
├── 📁 test/                    # Testes automatizados
├── 📁 help_devs/              # Ferramentas para desenvolvedores
├── 📄 main.py                  # Ponto de entrada
├── 📄 config.yaml             # Configuração principal
├── 📄 requirements.txt        # Dependências
├── 📄 README.md               # Documentação inicial
└── 📄 devstation.db           # Banco de dados SQLite
```

## Detalhamento por Diretório

### 1. `/core/` - Núcleo do Sistema

Diretório principal contendo toda a lógica de negócio e infraestrutura.

```
core/
├── 📄 __init__.py             # Inicialização do módulo
├── 📄 config.py               # Gerenciador de configuração
├── 📄 transaction.py          # Sistema de transações
├── 📄 plugin_manager.py       # Gerenciador de plugins
├── 📄 menu_manager.py         # Gerenciador de menus
├── 📄 audit_logger.py         # Sistema de auditoria
├── 📄 theme.py                # Gerenciador de temas
│
├── 📁 models/                 # Modelos de dados
│   ├── 📄 __init__.py
│   ├── 📄 base.py            # Modelo base SQLAlchemy
│   ├── 📄 user.py            # Modelo de usuário
│   ├── 📄 audit.py           # Modelo de auditoria
│   └── 📄 ... outros modelos
│
├── 📁 security/               # Sistema de segurança
│   ├── 📄 __init__.py
│   ├── 📄 auth.py            # Autenticação JWT
│   ├── 📄 rbac.py            # Controle de acesso
│   ├── 📄 models.py          # Modelos de segurança
│   ├── 📄 profile_manager.py # Gerenciador de perfis
│   └── 📄 dynamic_profiles.py # Perfis dinâmicos
│
└── 📁 kpi/                    # Métricas e indicadores
    ├── 📄 __init__.py
    └── 📄 collector.py       # Coletor de KPIs
```

#### Arquivos Principais do Core:

- **`config.py`**: Carrega configurações do `config.yaml` e variáveis de ambiente
- **`transaction.py`**: Define e executa transações do sistema
- **`plugin_manager.py`**: Gerencia ciclo de vida dos plugins
- **`audit_logger.py`**: Registra todas as ações para auditoria
- **`menu_manager.py`**: Controla menus dinâmicos baseados em permissões

### 2. `/ui/` - Componentes de Interface

Componentes reutilizáveis da interface do usuário.

```
ui/
├── 📄 __init__.py
├── 📄 app.py                  # Configuração principal da app
├── 📄 layout.py               # Layouts principais
├── 📄 components.py           # Componentes compartilhados
├── 📄 forms.py               # Componentes de formulário
├── 📄 tables.py              # Componentes de tabela
└── 📄 dialogs.py             # Diálogos e modais
```

#### Componentes Disponíveis:

- **`components.py`**: Botões, cards, badges, avatares
- **`forms.py`**: Inputs, selects, checkboxes, validadores
- **`tables.py`**: Tabelas paginadas, ordenáveis, filtros
- **`dialogs.py`**: Confirmações, formulários em modal

### 3. `/views/` - Views/Páginas

Views específicas da aplicação organizadas por funcionalidade.

```
views/
├── 📄 __init__.py
├── 📄 dashboard.py           # Página inicial/dashboard
├── 📄 login.py              # Página de login
├── 📄 profile.py            # Perfil do usuário
│
├── 📁 admin/                # Views administrativas
│   ├── 📄 __init__.py
│   ├── 📄 users.py         # Gerenciamento de usuários
│   ├── 📄 profiles.py      # Gerenciamento de perfis
│   ├── 📄 permissions.py   # Gerenciamento de permissões
│   └── 📄 audit.py         # Visualização de auditoria
│
└── 📁 tools/                # Ferramentas
    ├── 📄 __init__.py
    ├── 📄 query.py         # Console de queries
    └── 📄 gen_trans.py     # Gerador de transações
```

### 4. `/plugins/` - Plugins do Sistema

Plugins que estendem a funcionalidade do sistema.

```
plugins/
├── 📄 __init__.py
├── 📄 example_plugin/       # Exemplo de plugin
│   ├── 📄 __init__.py
│   ├── 📄 plugin.py        # Implementação principal
│   ├── 📄 views.py         # Views do plugin
│   └── 📄 requirements.txt # Dependências do plugin
│
└── 📄 ... outros plugins
```

#### Estrutura de um Plugin:

```python
# plugin.py
from core.plugin_manager import BasePlugin

class ExamplePlugin(BasePlugin):
    name = "Example Plugin"
    version = "1.0.0"
    description = "Plugin de exemplo"
    
    def initialize(self):
        # Inicialização do plugin
        pass
    
    def register_routes(self):
        # Registro de rotas/views
        pass
```

### 5. `/test/` - Testes Automatizados

Testes organizados por módulo.

```
test/
├── 📄 __init__.py
├── 📄 conftest.py           # Configuração do pytest
├── 📄 test_config.py        # Testes de configuração
│
├── 📁 core/                 # Testes do core
│   ├── 📄 __init__.py
│   ├── 📄 test_config.py
│   ├── 📄 test_transaction.py
│   └── 📁 security/        # Testes de segurança
│       ├── 📄 __init__.py
│       ├── 📄 test_auth.py
│       └── 📄 test_rbac.py
│
├── 📁 ui/                   # Testes de UI
│   ├── 📄 __init__.py
│   └── 📄 test_components.py
│
└── 📁 integration/          # Testes de integração
    ├── 📄 __init__.py
    └── 📄 test_plugins.py
```

### 6. `/help_devs/` - Ferramentas para Desenvolvedores

Scripts e ferramentas úteis para desenvolvimento.

```
help_devs/
├── 📄 create_users.py       # Cria usuários de teste
├── 📄 db_migrations.py      # Utilidades de migração
├── 📄 plugin_generator.py   # Gerador de plugins
└── 📄 ... outras ferramentas
```

## Arquivos na Raiz

### `main.py`
Ponto de entrada da aplicação. Responsável por:
- Inicializar a aplicação NiceGUI
- Configurar rotas e middlewares
- Iniciar o servidor web

```python
from nicegui import ui
from ui.app import create_app

if __name__ == "__main__":
    create_app()
    ui.run(
        title="DevStationPlatform",
        port=8080,
        reload=True  # Hot reload para desenvolvimento
    )
```

### `config.yaml`
Arquivo de configuração principal em YAML:

```yaml
app:
  name: "DevStationPlatform"
  version: "1.0.0"
  debug: true
  environment: "development"

database:
  dialect: "sqlite"
  database: "devstation.db"

security:
  jwt_secret_key: "CHANGE_ME_IN_PRODUCTION"
  jwt_expiration_hours: 24

# ... outras configurações
```

### `requirements.txt`
Lista de dependências Python:

```
nicegui>=1.4.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pyjwt>=2.0.0
bcrypt>=4.0.0
python-dotenv>=1.0.0
alembic>=1.0.0
```

### `devstation.db`
Banco de dados SQLite padrão para desenvolvimento. Contém:
- Tabelas de usuários, perfis, permissões
- Logs de auditoria
- Dados de configuração

## Convenções de Nomenclatura

### Arquivos Python
- **Snake case**: `user_manager.py`, `audit_logger.py`
- **Nomes descritivos**: Evitar abreviações obscuras
- **Sufixos claros**: `_test.py` para testes, `_view.py` para views

### Diretórios
- **Singular para módulos**: `core/`, `ui/`, `test/`
- **Plural para coleções**: `views/`, `plugins/`, `models/`
- **Nomes curtos e claros**: Evitar diretórios muito aninhados

### Classes
- **PascalCase**: `UserManager`, `AuditLogger`, `BasePlugin`
- **Sufixos para tipos**: `Manager`, `Service`, `Handler`, `View`

### Variáveis e Funções
- **snake_case**: `get_user_by_id()`, `validate_password()`
- **Verbos para funções**: `create_`, `update_`, `delete_`, `get_`
- **Adjetivos para booleanos**: `is_active`, `has_permission`

## Organização de Código

### 1. Imports
```python
# 1. Imports padrão Python
import os
import sys
from datetime import datetime

# 2. Imports de terceiros
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

# 3. Imports locais
from core.models.base import Base
from core.security.auth import authenticate_user
```

### 2. Estrutura de um Módulo
```python
"""Módulo: Descrição breve do módulo."""

# Imports
# Constantes
# Classes
# Funções
# Código de execução (se houver)
```

### 3. Documentação
```python
class UserManager:
    """Gerencia operações relacionadas a usuários.
    
    Attributes:
        db_session: Sessão do banco de dados
        audit_logger: Logger para auditoria
    """
    
    def create_user(self, username: str, password: str) -> User:
        """Cria um novo usuário no sistema.
        
        Args:
            username: Nome de usuário único
            password: Senha em texto claro (será hashada)
            
        Returns:
            Objeto User criado
            
        Raises:
            ValueError: Se username já existir
        """
        # Implementação
```

## Fluxo de Adição de Novos Recursos

### 1. Nova Funcionalidade no Core
```
1. Criar arquivo em core/ ou subdiretório apropriado
2. Definir classes/funções seguindo convenções
3. Adicionar imports em core/__init__.py se necessário
4. Criar testes em test/core/
5. Atualizar documentação
```

### 2. Nova View
```
1. Criar arquivo em views/ ou subdiretório
2. Herdar de BaseView se disponível
3. Registrar rota em ui/app.py
4. Adicionar ao menu em config.yaml se necessário
5. Criar testes em test/views/
```

### 3. Novo Plugin
```
1. Criar diretório em plugins/nome_plugin/
2. Implementar classe herdando de BasePlugin
3. Adicionar views específicas do plugin
4. Criar requirements.txt para dependências
5. Testar carregamento do plugin
```

## Ferramentas de Desenvolvimento

### 1. Scripts Úteis
```bash
# Criar usuário de teste
python help_devs/create_users.py

# Gerar novo plugin
python help_devs/plugin_generator.py MeuPlugin

# Verificar estilo de código
flake8 core/ --max-line-length=88

# Formatar código
black core/ views/ ui/
```

### 2. Comandos Git
```bash
# Estrutura de branches
git checkout -b feature/nova-funcionalidade
git checkout -b fix/correcao-bug
git checkout -b docs/atualizacao-documentacao

# Commits semânticos
git commit -m "feat: adiciona sistema de auditoria"
git commit -m "fix: corrige validação de senha"
git commit -m "docs: atualiza guia de instalação"
```

## Próximos Passos

1. [Configurar ambiente de desenvolvimento](./01_configuracao.md)
2. [Explorar APIs disponíveis](./03_api_integracoes.md)
3. [Entender arquitetura do core](../03_core_sistema/01_arquitetura_core.md)

---

**Última Atualização**: 2026-04-14  
**Total de Arquivos**: ~73 arquivos Python  
**Linhas de Código**: ~5,000 (estimado)  
**Test Coverage**: 85% (meta)