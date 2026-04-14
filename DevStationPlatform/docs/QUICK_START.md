# Quick Start DevStationPlatform

## 🚀 Comece em 5 Minutos

### 1. Instalação Rápida
```bash
# Clone (se aplicável)
# cd para o diretório do projeto

# Ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# Banco inicial
python help_devs/init_db.py

# Executar
python main.py
```

### 2. Acesse a Aplicação
- **URL**: http://localhost:8080
- **Usuários de Teste**:
  - admin / admin123 → Acesso total (ADMIN)
  - dev / dev123 → Desenvolvedor (DEVELOPER)
  - user / user123 → Usuário básico (USER)

### 3. Primeiros Passos
1. **Login** com `admin / admin123`
2. **Explore o Dashboard** → Visão geral do sistema
3. **Teste o Query Console** → `/tools/query`
4. **Verifique Usuários** → `/admin/users`
5. **Veja os Logs** → `/admin/audit`

## 📁 Estrutura do Projeto em 1 Minuto

```
DevStationPlatform/
├── core/           # 🏗️ Núcleo da plataforma
├── ui/             # 🎨 Interface (NiceGUI)
├── views/          # 🧩 Componentes visuais
├── plugins/        # 🔌 Sistema de plugins
├── docs/           # 📚 Documentação
├── config.yaml     # ⚙️ Configuração
└── main.py         # 🚪 Ponto de entrada
```

**Regra de Ouro**: Core (infra) não importa UI, mas UI pode importar Core.

## 🔧 Como Adicionar Nova Funcionalidade

### Exemplo: Adicionar "Exportar CSV"

#### 1. Criar Transação (Core)
```python
# core/transactions/export.py
from core.transaction import transaction

@transaction("DS_EXPORT_CSV")
def export_to_csv(data, filename):
    """Exporta dados para CSV"""
    import csv
    # Lógica de exportação...
    return "sucesso"
```

#### 2. Adicionar Permissão
```yaml
# config.yaml (security.default_permissions)
- code: "data.export.csv"
  name: "Exportar para CSV"
  category: "DATA"
```

#### 3. Criar Tela (UI)
```python
# ui/pages/tools_export.py
from nicegui import ui

def render():
    ui.label("Exportar para CSV")
    # Interface aqui...
```

#### 4. Adicionar Rota
```python
# ui/app.py
@ui.page('/tools/export')
def tools_export_page():
    tools_export.render()
```

#### 5. Adicionar ao Menu
```yaml
# config.yaml (menu.structure)
- label: "Exportar CSV"
  path: "/tools/export"
  transaction: "DS_EXPORT_CSV"
  permissions: ["data.export.csv"]
```

## 🧩 Criando um Plugin Simples

### Estrutura Mínima
```
plugins/
└── meu_plugin/
    ├── __init__.py
    └── manifest.yaml
```

### __init__.py
```python
class MeuPlugin:
    name = "Meu Plugin"
    version = "1.0.0"
    
    def register(self, plugin_manager):
        print(f"Plugin {self.name} registrado!")
        
    def enable(self):
        print("Plugin ativado!")
        
    def disable(self):
        print("Plugin desativado!")
```

### manifest.yaml
```yaml
name: "Meu Plugin"
version: "1.0.0"
author: "Você"
description: "Plugin de exemplo"
```

## 🎯 Transações em 30 Segundos

### Opção 1: Decorador (Recomendado)
```python
from core.transaction import transaction

@transaction("DS_MINHA_TRANSACAO")
def minha_funcao(param1, param2):
    """Descrição da transação"""
    resultado = param1 + param2
    return resultado

# Uso
resultado = minha_funcao(10, 20)
# ✅ Auditado automaticamente
# ✅ Métricas coletadas
# ✅ Permissões validadas
```

### Opção 2: Context Manager
```python
from core.transaction import Transaction

with Transaction("DS_COMPLEXA") as tx:
    resultado = processamento_complexo()
    tx.add_context("etapa", "finalizada")
    return resultado
# ✅ Rollback automático em erro
```

## 🔐 Sistema de Permissões

### Hierarquia de Perfis
```
ADMIN (100) → DEV_ALL → CORE_DEV → DEVELOPER → BANALYST → PUSER → USER (10)
```

### Verificar Permissão
```python
from core.security.rbac import rbac

# No core
tem_permissao = rbac.has_permission(user_id, "transaction.execute")

# Na UI (decorador)
from ui.app import requires_permission

@requires_permission("admin.users")
def pagina_admin():
    ui.label("Apenas para administradores")
```

## 🐛 Depuração Rápida

### Logs Importantes
```bash
# Log geral
tail -f logs/app.log

# Auditoria (JSON)
tail -f logs/audit.log

# Erros
tail -f logs/error.log
```

### Problemas Comuns

#### 1. Banco Bloqueado
```bash
# Verificar
lsof devstation.db

# Recriar (cuidado!)
rm devstation.db
python help_devs/init_db.py
```

#### 2. Plugin Não Carrega
1. Verifique estrutura do diretório
2. Confira `__init__.py` com classe principal
3. Verifique logs do plugin manager

#### 3. Autenticação Falha
1. Verifique `config.yaml` → `security.jwt_secret_key`
2. Confira tabela `users` no banco
3. Verifique logs de autenticação

## ⚡ Comandos Úteis

### Desenvolvimento
```bash
# Executar com hot reload
python main.py

# Criar usuários de teste
python help_devs/create_users.py

# Verificar estrutura do banco
python help_devs/check_users.py

# Limpar logs
rm -rf logs/*.log
```

### Testes
```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=core --cov=ui

# Testes específicos
pytest test/unit/core/
```

## 📊 Monitoramento

### Dashboard KPI
Acesse `/dashboard` para ver:
- Transações por minuto
- Taxa de sucesso/erro
- Usuários ativos
- Tempos de resposta

### Auditoria em Tempo Real
Acesse `/admin/audit` para:
- Ver logs recentes
- Filtrar por usuário/transação
- Exportar dados
- Buscar eventos específicos

## 🚀 Produção

### Configuração Mínima
```yaml
# config.yaml
app:
  debug: false  # IMPORTANTE!
  environment: "production"

security:
  jwt_secret_key: "${JWT_SECRET}"  # Use variável de ambiente!
  jwt_expiration_hours: 8

database:
  dialect: "postgresql"  # Não use SQLite em produção!
```

### Variáveis de Ambiente
```bash
# .env (não versionar!)
JWT_SECRET=chave_aleatoria_muito_forte
DB_PASSWORD=senha_forte_do_banco
```

### Executar com Gunicorn
```bash
gunicorn main:app --workers 4 --bind 0.0.0.0:8080
```

## ❓ Onde Encontrar Ajuda

### Documentação
1. `docs/ARCHITECTURE_GUIDE.md` → Arquitetura detalhada
2. `docs/DEVELOPER_GUIDE.md` → Guia completo
3. `docs/API_REFERENCE.md` → Referência de API
4. `docs/WORKFLOW_DIAGRAMS.md` → Diagramas de fluxo

### Código de Exemplo
1. `core/transaction.py` → Transações
2. `ui/pages/login.py` → Tela de login
3. `core/security/rbac.py` → Sistema RBAC
4. `core/plugin_manager.py` → Plugins

### Ferramentas de Ajuda
1. `help_devs/init_db.py` → Inicializar banco
2. `help_devs/create_users.py` → Criar usuários
3. `help_devs/check_users.py` → Verificar usuários

## 🎉 Próximos Passos

1. **Explore o código**: Comece por `main.py` e `ui/app.py`
2. **Teste as funcionalidades**: Use os usuários de teste
3. **Crie uma transação simples**: Siga o exemplo acima
4. **Desenvolva um plugin**: Use a estrutura mínima
5. **Contribua**: Melhore documentação, reporte bugs, sugira features

**Dica**: Sempre use `@transaction` para novas funcionalidades - garante rastreabilidade automática!

---

💡 **Lembrete**: Esta plataforma é inspirada em SAP com foco em rastreabilidade total. Tudo é auditado, tudo é mensurável, tudo é controlável por permissões.