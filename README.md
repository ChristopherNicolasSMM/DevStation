# DevStation

Sistema modular de gerenciamento de dados via planilhas Excel com auditoria, controle de acesso granular e CRUD configurável.

## Status do Projeto

### ✅ Fases Implementadas

- **Fase 1: Estrutura Base e Autenticação** - Completa
  - Sistema de autenticação com Flask-Login
  - Modelo de usuário com grupos (Administrador, Auditor, Operador, Visualizador)
  - Configuração de banco SQLite/PostgreSQL
  - Templates básicos de login e dashboard

- **Fase 2: Sistema de Configuração de Tabelas Dinâmicas** - Completa
  - Modelos TableConfig e FieldConfig
  - Criação dinâmica de tabelas no banco
  - Interface de administração para criar/editar tabelas e campos
  - Suporte a diferentes tipos de campos (text, number, date, boolean, list)

- **Fase 3: Sistema de Permissões Granular** - Completa
  - Modelo Permission com permissões por tabela e campo
  - Serviço de verificação de permissões
  - Decorators para proteção de rotas
  - Permissões por usuário e grupo

- **Fase 4: CRUD Genérico Configurável** - Completa
  - Serviço CRUD genérico
  - Rotas web e API REST
  - Templates reutilizáveis (list, create, edit, view)
  - Validação baseada em configuração
  - Filtros dinâmicos
  - Paginação
  - Respeito a permissões de visualização e edição

- **Fase 5: Sistema de Upload e Auditoria Excel** - Completa
  - Upload de arquivos Excel/CSV
  - Mapeamento de colunas Excel → campos
  - Detecção de divergências (novos, atualizações, sem alterações)
  - Painel de aprovação seletiva por campo
  - Histórico completo de importações

- **Fase 6: Sistema de Layouts e Filtros Avançados** - Completa
  - Modelo Layout com hierarquia (pessoal > grupo > padrão)
  - Salvamento de layouts (filtros, ordenação, colunas visíveis)
  - Aplicação automática de layouts na listagem

- **Fase 7: Sistema de Exportação** - Completa
  - Exportação para Excel (com formatação)
  - Exportação para PDF (relatórios formatados)
  - Exportação para CSV
  - Respeito a permissões de visualização

- **Fase 8: Dashboard e Administração** - Completa
  - Dashboard com estatísticas do sistema
  - Histórico de importações recentes
  - Painel de administração completo

- **Fase 9: Otimizações e Preparação para .exe** - Completa
  - Scripts de build para PyInstaller
  - Configuração pyinstaller.spec
  - Documentação de deploy (local e VPS)

## Instalação

```bash
# Criar ambiente virtual
python -m venv vEnvStation

# Ativar ambiente (Windows)
.\vEnvStation\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de configuração
copy src\config.env.modelo src\.env

# Executar aplicação
python run.py start
```

Acesse `http://localhost:5000` com:
- Usuário: `admin`
- Senha: `123`

## Estrutura do Projeto

```
DevStation/
├── src/
│   ├── api/              # Rotas REST API
│   ├── controller/       # Rotas web
│   ├── db/               # Configuração de banco
│   ├── model/            # Modelos SQLAlchemy
│   ├── services/         # Serviços de negócio
│   ├── templates/        # Templates HTML
│   ├── utils/            # Utilitários
│   └── main.py           # Application factory
├── requirements.txt
└── run.py
```

## Funcionalidades Principais

### 1. Criação Dinâmica de Tabelas

- Interface web para criar tabelas sem codificação
- Definição de campos com tipos, validações e regras
- Criação automática de tabelas no banco de dados
- Suporte a chaves únicas simples ou compostas

### 2. Sistema de Permissões

- Permissões por tabela (CREATE, READ, UPDATE, DELETE)
- Permissões por campo (VISIBLE, EDITABLE)
- Grupos de usuários com permissões padrão
- Herança de permissões (grupo → usuário)

### 3. CRUD Genérico

- Listagem com paginação e filtros
- Criação, edição e exclusão de registros
- Validação automática baseada em configuração
- Respeito a permissões de visualização e edição
- API REST completa

## Funcionalidades Implementadas

### ✅ Sistema Completo

1. **Criação Dinâmica de Tabelas** - Interface web para criar tabelas sem codificação
2. **Sistema de Permissões Granular** - Controle por tabela e campo
3. **CRUD Genérico** - Operações completas com validação e filtros
4. **Upload e Auditoria Excel** - Processamento com aprovação seletiva
5. **Layouts Salvos** - Configurações personalizadas por usuário/grupo
6. **Exportação** - Excel, PDF e CSV
7. **Dashboard** - Estatísticas e monitoramento
8. **Preparação para Deploy** - Scripts para .exe e VPS

## Próximos Passos (Opcional)

1. Testes unitários e de integração
2. Interface de gerenciamento de permissões mais visual
3. Melhorias na interface de layouts
4. Sistema de notificações
5. API REST completa documentada

## Documentação

A documentação completa será adicionada conforme as fases são implementadas.

## Licença

Este projeto é privado e de uso interno.
