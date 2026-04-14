# Configuração do Ambiente de Desenvolvimento

Este guia descreve como configurar o ambiente de desenvolvimento para o DevStationPlatform.

## Pré-requisitos

### 1. Sistema Operacional
- **Windows 10/11**, **Linux** (Ubuntu 20.04+, CentOS 7+), ou **macOS** 10.15+
- Terminal com suporte a bash/zsh
- Permissões de administrador para instalação de pacotes

### 2. Python
- **Python 3.10 ou superior**
- Verifique a versão:
  ```bash
  python --version
  # ou
  python3 --version
  ```

### 3. Gerenciador de Pacotes
- **pip** (vem com Python)
- **Poetry** (recomendado) ou **venv** para ambientes virtuais

### 4. Git
- **Git 2.25+**
- Configure usuário e email:
  ```bash
  git config --global user.name "Seu Nome"
  git config --global user.email "seu.email@exemplo.com"
  ```

## Instalação Passo a Passo

### Opção 1: Usando Poetry (Recomendado)

#### 1. Instalar Poetry
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Adicionar ao PATH (se necessário)
export PATH="$HOME/.local/bin:$PATH"
```

#### 2. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/DevStationPlatform.git
cd DevStationPlatform
```

#### 3. Configurar Ambiente Virtual
```bash
# Criar ambiente virtual com Python 3.10
poetry env use python3.10

# Ativar ambiente
poetry shell

# Instalar dependências
poetry install

# Instalar dependências de desenvolvimento
poetry install --with dev
```

#### 4. Verificar Instalação
```bash
# Verificar dependências instaladas
poetry show

# Testar importação do core
python -c "from core.config import Config; print('Configuração carregada com sucesso')"
```

### Opção 2: Usando venv + pip

#### 1. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/DevStationPlatform.git
cd DevStationPlatform
```

#### 2. Criar Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependências
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências principais
pip install -r requirements.txt

# Instalar dependências de desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

## Configuração do Projeto

### 1. Arquivo de Configuração

O arquivo `config.yaml` na raiz do projeto contém todas as configurações:

```yaml
app:
  name: "DevStationPlatform"
  version: "1.0.0"
  debug: true  # Alterar para false em produção
  environment: "development"  # development, staging, production

database:
  dialect: "sqlite"  # sqlite, postgresql, mysql
  database: "devstation.db"  # Nome do arquivo ou banco
  echo: false  # Log de queries SQL
  pool_size: 5
  max_overflow: 10

# ... outras configurações
```

### 2. Configurações por Ambiente

Crie arquivos de configuração específicos:

```bash
# Configuração desenvolvimento
cp config.yaml config.dev.yaml

# Configuração produção
cp config.yaml config.prod.yaml
```

### 3. Variáveis de Ambiente

Configure variáveis sensíveis via ambiente:

```bash
# Linux/macOS
export DEVSTATION_JWT_SECRET="sua_chave_secreta"
export DEVSTATION_DB_URL="postgresql://user:pass@localhost/devstation"

# Windows (PowerShell)
$env:DEVSTATION_JWT_SECRET="sua_chave_secreta"
$env:DEVSTATION_DB_URL="postgresql://user:pass@localhost/devstation"
```

Ou crie um arquivo `.env`:

```env
# .env
DEVSTATION_JWT_SECRET=sua_chave_secreta_aqui
DEVSTATION_DB_URL=sqlite:///devstation.db
DEVSTATION_DEBUG=true
DEVSTATION_ENVIRONMENT=development
```

## Banco de Dados

### 1. SQLite (Padrão para Desenvolvimento)

Nenhuma configuração adicional necessária. O banco será criado automaticamente:

```bash
# O arquivo devstation.db será criado na primeira execução
python main.py
```

### 2. PostgreSQL (Recomendado para Produção)

#### Instalar PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows: Baixar do site oficial
```

#### Configurar Banco:
```sql
-- Conectar como postgres
sudo -u postgres psql

-- Criar banco de dados
CREATE DATABASE devstation;

-- Criar usuário
CREATE USER devstation_user WITH PASSWORD 'senha_segura';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE devstation TO devstation_user;

-- Sair
\q
```

#### Atualizar Configuração:
```yaml
database:
  dialect: "postgresql"
  database: "devstation"
  username: "devstation_user"
  password: "senha_segura"
  host: "localhost"
  port: 5432
```

### 3. MySQL

#### Instalar MySQL:
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS
brew install mysql

# Windows: MySQL Installer
```

#### Configurar Banco:
```sql
-- Acessar MySQL
mysql -u root -p

-- Criar banco de dados
CREATE DATABASE devstation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário
CREATE USER 'devstation_user'@'localhost' IDENTIFIED BY 'senha_segura';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON devstation.* TO 'devstation_user'@'localhost';
FLUSH PRIVILEGES;

-- Sair
EXIT;
```

#### Atualizar Configuração:
```yaml
database:
  dialect: "mysql"
  database: "devstation"
  username: "devstation_user"
  password: "senha_segura"
  host: "localhost"
  port: 3306
```

## Executando a Aplicação

### 1. Modo Desenvolvimento
```bash
# Com recarregamento automático
python main.py

# Ou especificando porta
python main.py --port 8080 --reload
```

### 2. Modo Produção
```bash
# Desativar debug
# Editar config.yaml: debug: false

# Executar com gunicorn (se configurado)
gunicorn main:app --workers 4 --bind 0.0.0.0:8080
```

### 3. Verificar Execução
Acesse no navegador: `http://localhost:8080`

## Configuração do Editor/IDE

### Visual Studio Code

#### Extensões Recomendadas:
- **Python** (Microsoft)
- **Pylance** (Type checking)
- **Black Formatter** (Formatação)
- **Flake8** (Linting)
- **SQLite** (Visualizar banco)

#### Configurações do Workspace (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true
  }
}
```

### PyCharm

#### Configurações:
1. **File > Settings > Project > Python Interpreter**
   - Selecione o ambiente virtual (`venv` ou Poetry)
2. **Tools > Python Integrated Tools**
   - Test runner: pytest
   - Docstring format: Google
3. **Editor > Code Style > Python**
   - Line length: 88
   - Usar Black se instalado

## Ferramentas de Desenvolvimento

### 1. Testes
```bash
# Executar todos os testes
pytest

# Executar testes específicos
pytest tests/core/test_security.py

# Com cobertura
pytest --cov=core --cov-report=html

# Testes em paralelo
pytest -n auto
```

### 2. Linting e Formatação
```bash
# Verificar estilo
flake8 core/ tests/

# Formatar código
black core/ tests/

# Ordenar imports
isort core/ tests/
```

### 3. Type Checking
```bash
# Verificar tipos
mypy core/
```

### 4. Segurança
```bash
# Verificar vulnerabilidades
pip-audit

# Análise estática de segurança
bandit -r core/
```

## Solução de Problemas Comuns

### 1. Erro: "ModuleNotFoundError"
```bash
# Verificar se ambiente está ativado
which python  # Linux/macOS
where python  # Windows

# Reinstalar dependências
poetry install --sync
# ou
pip install -r requirements.txt
```

### 2. Erro de Conexão com Banco
```bash
# Verificar se banco está rodando
# SQLite: arquivo devstation.db existe
# PostgreSQL: sudo systemctl status postgresql
# MySQL: sudo systemctl status mysql

# Verificar credenciais no config.yaml
```

### 3. Porta em Uso
```bash
# Encontrar processo usando a porta
# Linux/macOS
lsof -i :8080

# Windows
netstat -ano | findstr :8080

# Matar processo
kill <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### 4. Problemas com Dependências
```bash
# Limpar cache do pip
pip cache purge

# Reinstalar Poetry
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | python3 -

# Reconstruir ambiente
rm -rf venv/ .venv/
poetry env remove python
poetry install
```

## Configuração Avançada

### 1. Docker para Desenvolvimento

Crie um `docker-compose.dev.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
      - ./devstation.db:/app/devstation.db
    environment:
      - DEVSTATION_ENVIRONMENT=development
      - DEVSTATION_DEBUG=true
    command: python main.py --reload
```

### 2. Configuração de Proxy

Se estiver atrás de proxy corporativo:

```bash
# Configurar proxy para pip
pip config set global.proxy http://proxy.corporativo.com:8080

# Configurar proxy para git
git config --global http.proxy http://proxy.corporativo.com:8080
```

### 3. Monitoramento de Recursos

Instale ferramentas de monitoramento:

```bash
# Linux
sudo apt-get install htop

# Verificar uso de recursos
htop
# ou
ps aux | grep python
```

## Próximos Passos

1. [Explorar estrutura do projeto](./02_estrutura_projeto.md)
2. [Entender APIs disponíveis](./03_api_integracoes.md)
3. [Configurar ambiente de produção](../08_implantacao/01_ambientes.md)

---

**Última Atualização**: 2026-04-14  
**Ambiente Testado**: Windows 11, Ubuntu 22.04, macOS Ventura  
**Python Versões**: 3.10, 3.11, 3.12