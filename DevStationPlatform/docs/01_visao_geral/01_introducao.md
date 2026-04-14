# Introdução ao DevStationPlatform

## Visão Geral

O **DevStationPlatform** é uma plataforma RAD (Rapid Application Development) inspirada em sistemas empresariais como SAP, com foco em rastreabilidade total, segurança robusta e extensibilidade através de plugins.

### Objetivos Principais

1. **Produtividade**: Desenvolvimento rápido de aplicações empresariais
2. **Rastreabilidade**: Auditoria completa de todas as ações no sistema
3. **Segurança**: Controle de acesso granular baseado em perfis dinâmicos
4. **Extensibilidade**: Arquitetura baseada em plugins para fácil expansão
5. **Usabilidade**: Interface moderna e intuitiva baseada em NiceGUI

### Público-Alvo

- **Desenvolvedores**: Criar plugins e funcionalidades personalizadas
- **Analistas de Negócios**: Desenvolver transações e relatórios
- **Usuários Finais**: Executar transações e consultas
- **Administradores**: Gerenciar segurança e auditoria

## Características Principais

### 🚀 Desenvolvimento Rápido
- Interface baseada em NiceGUI para desenvolvimento web rápido
- Sistema de transações pré-configuradas
- Templates e componentes reutilizáveis

### 🔒 Segurança Avançada
- RBAC (Role-Based Access Control) com perfis dinâmicos
- Auditoria completa de todas as ações
- Autenticação JWT com expiração configurável
- Criptografia BCrypt para senhas

### 🔌 Extensibilidade Total
- Arquitetura baseada em plugins
- Hot-reload de plugins em desenvolvimento
- API clara para desenvolvimento de extensões
- Marketplace de plugins planejado

### 📊 Rastreabilidade Completa
- Log de auditoria de todas as transações
- Histórico de alterações em dados sensíveis
- KPIs de uso e performance
- Relatórios de atividade

### 🎨 Interface Moderna
- Temas claro/escuro
- Componentes responsivos
- Navegação intuitiva por menus hierárquicos
- Dashboard personalizável

## Casos de Uso

### 1. Desenvolvimento de Aplicações Empresariais
- CRUDs complexos com validações
- Relatórios e dashboards
- Integrações com sistemas legados
- Workflows de aprovação

### 2. Plataforma de Desenvolvimento Interna
- Ferramentas para equipes de desenvolvimento
- Consoles de query e debug
- Geradores de código
- Testes de integração

### 3. Sistema de Gestão
- Controle de acesso granular
- Auditoria de compliance
- Gestão de usuários e perfis
- Monitoramento de atividades

## Tecnologias Utilizadas

### Backend
- **Python 3.10+**: Linguagem principal
- **NiceGUI**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **JWT**: Autenticação por tokens

### Banco de Dados
- **SQLite**: Banco padrão (desenvolvimento)
- **PostgreSQL/MySQL**: Suporte para produção
- **Alembic**: Migrações de banco

### Frontend
- **Vue.js 3**: Framework JavaScript (via NiceGUI)
- **Tailwind CSS**: Estilização
- **Quasar**: Componentes UI

### Ferramentas de Desenvolvimento
- **Poetry**: Gerenciamento de dependências
- **Pytest**: Testes automatizados
- **Black/Flake8**: Formatação e linting
- **Docker**: Containerização

## Arquitetura Geral

O sistema segue uma arquitetura modular com as seguintes camadas:

```
┌─────────────────────────────────┐
│        Interface Web (NiceGUI)  │
├─────────────────────────────────┤
│        Camada de Views          │
├─────────────────────────────────┤
│        Core do Sistema          │
│  • Segurança                    │
│  • Transações                   │
│  • Plugins                      │
│  • Auditoria                    │
├─────────────────────────────────┤
│        Camada de Dados          │
│  • Models SQLAlchemy            │
│  • Repositórios                 │
└─────────────────────────────────┘
```

## Próximos Passos

1. [Configurar ambiente de desenvolvimento](../02_guia_desenvolvedor/01_configuracao.md)
2. [Explorar a arquitetura do sistema](./02_arquitetura.md)
3. [Entender os requisitos](./03_requisitos.md)

---

**Versão**: 1.0.0  
**Última atualização**: 2026-04-14  
**Status**: Em desenvolvimento ativo