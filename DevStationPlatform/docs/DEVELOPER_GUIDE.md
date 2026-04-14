# Guia do Desenvolvedor DevStationPlatform

## Índice
1. [Primeiros Passos](#primeiros-passos)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Como Adicionar Nova Funcionalidade](#como-adicionar-nova-funcionalidade)
4. [Criando uma Transação](#criando-uma-transação)
5. [Desenvolvendo Plugins](#desenvolvendo-plugins)
6. [Testes e Qualidade](#testes-e-qualidade)
7. [Depuração e Troubleshooting](#depuração-e-troubleshooting)
8. [Deploy e Produção](#deploy-e-produção)

## 1. Primeiros Passos

### 1.1 Ambiente de Desenvolvimento
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd DevStationPlatform

# Ambiente virtual
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# Banco de dados inicial
python help_devs/init_db.py

# Executar aplicação
python main.py
```

### 1.2 Usuários de Teste
O sistema cria automaticamente usuários de teste:
- **admin** / admin123 → Perfil ADMIN (acesso total)
- **dev** / dev123 → Perfil DEVELOPER
- **user** / user123 → Perfil USER

### 1.3 Acesso à Aplicação
- **URL**: http://localhost:8080
- **Login**: Use credenciais acima
- **Dashboard**: Visão geral após login

## 2. Estrutura do Projeto

### 2.1 Visão Geral
```
DevStationPlatform/
├── core/                    # Núcleo da plataforma
│   ├── config.py           # Configuração central
│   ├── security/           # RBAC e autenticação
│   ├── models/             # Modelos de dados
│   ├── plugin_manager.py   # Sistema de plugins
│   ├── transaction.py      # Sistema de transações
│   ├── audit_logger.py     # Logger de auditoria
│   └── kpi/                # Coletor de métricas
├── ui/                     # Interface (NiceGUI)
│   ├── app.py             # App principal e rotas
│   └── pages/             # Telas da aplicação
├── views/                  # Componentes visuais
│   ├── components/        # Componentes reutilizáveis
│   └── *.py               # Views complexas
├── plugins/               # Plugins da plataforma
├── docs/                  # Documentação
├── help_devs/            # Scripts de desenvolvimento
├── test/                  # Testes automatizados
├── config.yaml           # Configuração YAML
├── main.py               # Ponto de entrada
└── requirements.txt      # Dependências Python
```

### 2.2 O Que é Core vs UI
| **Core (Infraestrutura)** | **UI (Interface)** |
|---------------------------|-------------------|
| Lógica de negócio | Apresentação visual |
| Banco de dados | Componentes HTML/CSS |
| Segurança (RBAC) | Rotas e navegação |
| Transações | Formulários e inputs |
| Plugins | Temas e estilos |
| Auditoria | Interação do usuário |

**Regra**: Core não deve importar UI, mas UI pode importar Core.

## 3. Como Adicionar Nova Funcionalidade

### 3.1 Processo Padrão
```
1. Analisar requisitos → Qual problema resolve?
2. Definir transação → Código único (ex: DS_NOVAFUNC)
3. Criar permissão → Quem pode acessar?
4. Implementar core → Lógica de negócio
5. Criar interface → Tela para usuário
6. Adicionar ao menu → Onde aparece?
7. Testar → Funcionalidade e segurança
8. Documentar → Como usar?
```

### 3.2 Exemplo: Adicionando Exportação CSV

#### Passo 1 - Definir Transação
```python
# core/transactions/export.py
from core.transaction import transaction

@transaction("DS_EXPORT_CSV")
def export_to_csv(data, filename):
    """Exporta dados para CSV"""
    # Lógica de exportação
    pass
```

#### Passo 2 - Criar Permissão
```yaml
# config.yaml (security.default_permissions)
- code: "data.export.csv"
  name: "Exportar para CSV"
  category: "DATA"
```

#### Passo 3 - Implementar UI
```python
# ui/pages/tools_export.py
from nicegui import ui
from core.transactions.export import export_to_csv

def render():
    ui.label("Exportar para CSV")
    # Interface do usuário
```

#### Passo 4 - Adicionar Rota
```python
# ui/app.py
@ui.page('/tools/export')
def tools_export_page():
    tools_export.render()
```

#### Passo 5 - Adicionar ao Menu
```yaml
# config.yaml (menu.structure)
- label: "Exportar CSV"
  path: "/tools/export"
  transaction: "DS_EXPORT_CSV"
  permissions: ["data.export.csv"]
```

## 4. Criando uma Transação

### 4.1 O Que é uma Transação?
Unidade básica de trabalho no DevStationPlatform que:
- É auditável automaticamente
- Coleta métricas (KPI)
- Valida permissões
- Pode ter rollback

### 4.2 Estrutura Básica
```python
from core.transaction import transaction
from core.audit_logger import audit_logger

@transaction("DS_MINHA_TRANSACAO")
def minha_funcao(param1, param2, user_id=None):
    """
    Descrição da transação.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
        user_id: ID do usuário (automático)
    
    Returns:
        Resultado da transação
    
    Raises:
        Exception: Em caso de erro
    """
    # Lógica da transação
    resultado = fazer_algo(param1, param2)
    
    # Log adicional (opcional)
    audit_logger.log_additional(
        transaction_code="DS_MINHA_TRANSACAO",
        details={"param1": param1, "resultado": resultado}
    )
    
    return resultado
```

### 4.3 Parâmetros Automáticos
O decorador `@transaction` injeta automaticamente:
- `user_id`: ID do usuário atual (se autenticado)
- `transaction_id`: ID único desta execução
- `start_time`: Timestamp de início

### 4.4 Tratamento de Erros
```python
@transaction("DS_TRANSACAO_COM_ERRO")
def transacao_com_erro():
    try:
        # Código que pode falhar
        resultado = codigo_instavel()
        return resultado
    except Exception as e:
        # Erro será registrado no audit log automaticamente
        # KPI marcará como falha
        raise  # Re-lança para tratamento na UI
```

### 4.5 Transações com Rollback
```python
from core.transaction import Transaction

def transacao_complexa():
    with Transaction("DS_TRANSACAO_COMPLEXA") as tx:
        # Operação 1
        resultado1 = operacao1()
        tx.add_to_context("op1_result", resultado1)
        
        # Operação 2 (depende de 1)
        resultado2 = operacao2(resultado1)
        
        # Se algo falhar, tudo é revertido
        return resultado2
```

## 5. Desenvolvendo Plugins

### 5.1 Estrutura de Plugin Mínima
```
plugins/
└── meu_plugin/
    ├── __init__.py          # Classe principal
    ├── manifest.yaml        # Metadados
    └── README.md           # Documentação
```

#### __init__.py
```python
class MeuPlugin:
    """Plugin de exemplo para DevStationPlatform"""
    
    name = "Meu Plugin"
    version = "1.0.0"
    author = "Seu Nome"
    description = "Descrição do plugin"
    
    def __init__(self):
        self.enabled = False
        
    def register(self, plugin_manager):
        """Registrar plugin no sistema"""
        self.plugin_manager = plugin_manager
        print(f"[Plugin] {self.name} v{self.version} registrado")
        
    def enable(self):
        """Ativar plugin"""
        self.enabled = True
        # Conectar hooks, adicionar rotas, etc.
        
    def disable(self):
        """Desativar plugin"""
        self.enabled = False
        # Desconectar hooks, remover rotas, etc.
```

#### manifest.yaml
```yaml
name: "Meu Plugin"
version: "1.0.0"
author: "Seu Nome"
description: "Descrição do plugin"
dependencies:
  - pandas>=1.5.0
  - numpy>=1.21.0
compatibility:
  min_core_version: "1.0.0"
  max_core_version: "2.0.0"
hooks:
  - on_app_start
  - on_user_login
```

### 5.2 Hooks Disponíveis
```python
class MeuPlugin:
    def register(self, plugin_manager):
        # Registrar hooks
        plugin_manager.register_hook("on_app_start", self.on_app_start)
        plugin_manager.register_hook("on_user_login", self.on_user_login)
        plugin_manager.register_hook("on_transaction_execute", self.on_transaction)
    
    def on_app_start(self, app):
        """Executado quando aplicação inicia"""
        print("Aplicação iniciada!")
        
    def on_user_login(self, user_data):
        """Executado após login de usuário"""
        print(f"Usuário {user_data['username']} fez login")
        
    def on_transaction(self, transaction_code, user_id, params):
        """Executado antes/depois de transação"""
        if transaction_code == "DS_QUERY":
            print(f"Consulta SQL executada por usuário {user_id}")
```

### 5.3 Adicionando Rotas ao Plugin
```python
from nicegui import ui

class MeuPlugin:
    def enable(self):
        # Adicionar rota customizada
        @ui.page('/meu-plugin/dashboard')
        def plugin_dashboard():
            ui.label(f"Dashboard do {self.name}")
            # Mais componentes...
```

### 5.4 Adicionando Itens ao Menu
```python
class MeuPlugin:
    def enable(self):
        # Adicionar item ao menu principal
        menu_item = {
            "label": "Meu Plugin",
            "icon": "extension",
            "path": "/meu-plugin/dashboard",
            "permissions": ["plugin.meuplugin.access"]
        }
        self.plugin_manager.add_menu_item(menu_item)
```

### 5.5 Boas Práticas para Plugins
1. **Isolamento**: Não modificar core diretamente
2. **Dependências**: Declarar em manifest.yaml
3. **Configuração**: Usar `plugin_manager.config`
4. **Logging**: Usar `plugin_manager.log()`
5. **Erros**: Tratar e reportar adequadamente
6. **Compatibilidade**: Verificar versão do core

## 6. Testes e Qualidade

### 6.1 Estrutura de Testes
```
test/
├── unit/                  # Testes unitários
│   ├── core/             # Testes do núcleo
│   ├── models/           # Testes de modelos
│   └── security/         # Testes de segurança
├── integration/          # Testes de integração
│   ├── api/             # Testes de API
│   └── ui/              # Testes de interface
├── fixtures/             # Dados de teste
└── conftest.py          # Configuração pytest
```

### 6.2 Executando Testes
```bash
# Todos os testes
pytest

# Testes específicos
pytest test/unit/core/
pytest test/integration/api/

# Com cobertura
pytest --cov=core --cov=ui

# Com relatório HTML
pytest --cov=core --cov-report=html
```

### 6.3 Testando Transações
```python
# test/unit/core/test_transactions.py
import pytest
from core.transaction import transaction

def test_transaction_success():
    """Testar transação bem-sucedida"""
    
    @transaction("DS_TEST")
    def transacao_teste():
        return "sucesso"
    
    resultado = transacao_teste()
    assert resultado == "sucesso"
    
def test_transaction_audit():
    """Verificar se transação gera log"""
    # Verificar se entrada foi criada no audit log
    pass
```

### 6.4 Testando Permissões
```python
# test/unit/security/test_rbac.py
def test_user_has_permission():
    """Verificar se usuário tem permissão"""
    from core.security.rbac import rbac
    
    # Criar usuário de teste
    user = create_test_user(profiles=["DEVELOPER"])
    
    # DEVELOPER deve ter permissão de transação
    assert rbac.has_permission(user, "transaction.execute")
    
    # DEVELOPER não deve ter permissão de admin
    assert not rbac.has_permission(user, "admin.users")
```

### 6.5 Testes de UI (NiceGUI)
```python
# test/integration/ui/test_login.py
def test_login_page():
    """Testar página de login"""
    # Simular acesso à página
    # Verificar elementos presentes
    # Testar submissão de formulário
    pass
```

## 7. Depuração e Troubleshooting

### 7.1 Logs do Sistema
```
logs/
├── app.log              # Log geral da aplicação
├── audit.log           # Logs de auditoria (JSON)
└── error.log           # Erros críticos
```

#### Níveis de Log
- **DEBUG**: Informações detalhadas (desenvolvimento)
- **INFO**: Eventos normais da aplicação
- **WARNING**: Situações anormais não críticas
- **ERROR**: Erros que afetam funcionalidade
- **CRITICAL**: Erros que impedem execução

### 7.2 Debug no Código
```python
import logging

logger = logging.getLogger(__name__)

def funcao_com_problema():
    logger.debug("Iniciando função")
    
    try:
        resultado = codigo_problematico()
        logger.info(f"Resultado: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Erro na função: {e}", exc_info=True)
        raise
```

### 7.3 Problemas Comuns

#### Banco de Dados Bloqueado
```bash
# Verificar se processo está usando o DB
lsof devstation.db

# Forçar unlock (cuidado!)
rm devstation.db
python help_devs/init_db.py
```

#### Autenticação Falhando
1. Verificar `config.yaml` → `security.jwt_secret_key`
2. Verificar banco → tabela `users` existe
3. Verificar logs → `logs/app.log`

#### Plugin Não Carrega
1. Verificar estrutura do diretório
2. Verificar `__init__.py` com classe principal
3. Verificar dependências instaladas
4. Verificar logs do plugin manager

### 7.4 Ferramentas de Depuração

#### NiceGUI Developer Tools
- **F12**: Console do navegador
- **Elementos**: Inspecionar componentes
- **Rede**: Verificar requisições HTTP
- **Console**: Logs do JavaScript

#### Python Debugger (PDB)
```python
import pdb

def funcao_com_bug():
    pdb.set_trace()  # Ponto de interrupção
    # Código para depurar
```

#### SQLAlchemy Echo
```python
# config.yaml
database:
  echo: true  # Log SQL no console
```

## 8. Deploy e Produção

### 8.1 Configuração para Produção
```yaml
# config.yaml (produção)
app:
  name: "DevStationPlatform"
  version: "1.0.0"
  debug: false  # IMPORTANTE!
  environment: "production"

database:
  dialect: "postgresql"
  host: "localhost"
  port: 5432
  database: "devstation_prod"
  user: "devstation_user"
  password: "${DB_PASSWORD}"  # Variável de ambiente

security:
  jwt_secret_key: "${JWT_SECRET}"  # NUNCA usar padrão!
  jwt_expiration_hours: 8
  session_timeout_minutes: 15

logging:
  level: "WARNING"
  file: "/var/log/devstation/app.log"
```

### 8.2 Variáveis de Ambiente
```bash
# .env (não versionar!)
DB_PASSWORD=senha_forte_aqui
JWT_SECRET=chave_secreta_aleatoria_aqui
```

### 8.3 Servidor de Produção (Gunicorn)
```bash
# requirements-prod.txt
gunicorn==20.1.0

# Executar
gunicorn main:app --workers 4 --bind 0.0.0.0:8080
```

### 8