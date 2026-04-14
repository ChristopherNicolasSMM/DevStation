# Diagrama de Arquitetura

## Diagrama de Alto Nível

```mermaid
graph TB
    subgraph "Camada de Apresentação"
        UI[Interface NiceGUI]
        Views[Views/Pages]
        Components[Componentes UI]
    end
    
    subgraph "Camada de Aplicação"
        Services[Services/Handlers]
        Transactions[Sistema de Transações]
        MenuManager[Gerenciador de Menus]
    end
    
    subgraph "Camada de Domínio"
        Core[Core Business]
        Security[Sistema de Segurança]
        Plugins[Gerenciador de Plugins]
        Audit[Sistema de Auditoria]
    end
    
    subgraph "Camada de Infraestrutura"
        DB[(Banco de Dados)]
        Config[Gerenciador de Config]
        Logger[Sistema de Logs]
    end
    
    UI --> Views
    Views --> Components
    Views --> Services
    Services --> Transactions
    Services --> MenuManager
    Transactions --> Core
    Transactions --> Security
    Transactions --> Audit
    Security --> DB
    Core --> DB
    Plugins --> Services
    Audit --> Logger
    Config --> DB
    Config --> Logger
```

## Diagrama de Componentes Detalhado

```mermaid
graph LR
    subgraph "Frontend"
        Browser[Navegador Web]
        NiceGUI[NiceGUI Framework]
        Vue[Vue.js Components]
    end
    
    subgraph "Backend - Python"
        subgraph "Web Layer"
            Main[main.py - Entry Point]
            Routes[Rotas/Endpoints]
            Middleware[Middleware Chain]
        end
        
        subgraph "Application Layer"
            TransactionService[Transaction Service]
            AuthService[Authentication Service]
            PluginService[Plugin Service]
            AuditService[Audit Service]
        end
        
        subgraph "Domain Layer"
            UserModel[User Model]
            ProfileModel[Profile Model]
            PermissionModel[Permission Model]
            BusinessRules[Business Rules]
        end
        
        subgraph "Infrastructure Layer"
            SQLAlchemy[SQLAlchemy ORM]
            ConfigManager[Config Manager]
            Logger[Structured Logger]
            Cache[(Cache Redis)]
        end
        
        subgraph "Data Layer"
            SQLite[(SQLite Dev)]
            PostgreSQL[(PostgreSQL Prod)]
            MySQL[(MySQL Alt)]
        end
    end
    
    Browser --> NiceGUI
    NiceGUI --> Vue
    NiceGUI --> Main
    Main --> Routes
    Routes --> Middleware
    Middleware --> AuthService
    AuthService --> TransactionService
    AuthService --> PluginService
    TransactionService --> BusinessRules
    PluginService --> BusinessRules
    BusinessRules --> UserModel
    BusinessRules --> ProfileModel
    BusinessRules --> PermissionModel
    UserModel --> SQLAlchemy
    ProfileModel --> SQLAlchemy
    PermissionModel --> SQLAlchemy
    SQLAlchemy --> SQLite
    SQLAlchemy --> PostgreSQL
    SQLAlchemy --> MySQL
    ConfigManager --> SQLAlchemy
    Logger --> AuditService
    AuditService --> SQLAlchemy
    TransactionService --> Cache
```

## Diagrama de Fluxo de Dados

```mermaid
sequenceDiagram
    participant U as Usuário
    participant V as View
    participant S as Service
    participant H as Transaction Handler
    participant R as Repository
    participant DB as Banco de Dados
    participant A as Audit Logger
    
    U->>V: 1. Submete Formulário
    V->>S: 2. Validação Básica
    S->>H: 3. Processa Transação
    H->>R: 4. Busca Dados
    R->>DB: 5. Executa Query
    DB-->>R: 6. Retorna Dados
    R-->>H: 7. Dados Processados
    H->>A: 8. Registra Auditoria
    H->>DB: 9. Persiste Alterações
    H-->>S: 10. Resultado
    S-->>V: 11. Resposta
    V-->>U: 12. Feedback UI
```

## Diagrama de Sistema de Segurança

```mermaid
graph TD
    subgraph "Authentication Flow"
        A1[Login Request] --> A2[Validate Credentials]
        A2 --> A3[Check Password BCrypt]
        A3 --> A4[Generate JWT Token]
        A4 --> A5[Return Token to Client]
    end
    
    subgraph "Authorization Flow"
        B1[API Request with JWT] --> B2[Verify JWT Signature]
        B2 --> B3[Decode Token Payload]
        B3 --> B4[Get User & Profiles]
        B4 --> B5[Check Permissions RBAC]
        B5 --> B6[Allow/Deny Access]
    end
    
    subgraph "Audit Trail"
        C1[Action Performed] --> C2[Log to Audit System]
        C2 --> C3[Store in Database]
        C3 --> C4[Generate Reports]
    end
    
    A5 --> B1
    B6 --> C1
```

## Diagrama de Plugin Architecture

```mermaid
graph TB
    subgraph "Core System"
        PM[Plugin Manager]
        PL[Plugin Loader]
        PH[Plugin Hook System]
    end
    
    subgraph "Plugin 1"
        P1[Plugin Class]
        P1V[Plugin Views]
        P1M[Plugin Models]
    end
    
    subgraph "Plugin 2"
        P2[Plugin Class]
        P2V[Plugin Views]
        P2M[Plugin Models]
    end
    
    subgraph "Plugin 3"
        P3[Plugin Class]
        P3V[Plugin Views]
        P3M[Plugin Models]
    end
    
    PM --> PL
    PL --> P1
    PL --> P2
    PL --> P3
    PH --> P1
    PH --> P2
    PH --> P3
    P1 --> P1V
    P1 --> P1M
    P2 --> P2V
    P2 --> P2M
    P3 --> P3V
    P3 --> P3M
    
    P1V --> UI[User Interface]
    P2V --> UI
    P3V --> UI
```

## Diagrama de Deployment

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Local Machine]
        DevDB[(SQLite)]
        DevCache[(Redis Dev)]
    end
    
    subgraph "Staging Environment"
        Stage[Staging Server]
        StageDB[(PostgreSQL Stage)]
        StageCache[(Redis Stage)]
        StageLB[Load Balancer]
    end
    
    subgraph "Production Environment"
        Prod1[App Server 1]
        Prod2[App Server 2]
        Prod3[App Server 3]
        ProdDB[(PostgreSQL Cluster)]
        ProdCache[(Redis Cluster)]
        ProdLB[Load Balancer]
        CDN[CDN]
        Monitor[Monitoring]
    end
    
    subgraph "CI/CD Pipeline"
        Git[Git Repository]
        CI[CI Server]
        Registry[Docker Registry]
        Deploy[Deployment]
    end
    
    Dev --> DevDB
    Dev --> DevCache
    
    StageLB --> Stage
    Stage --> StageDB
    Stage --> StageCache
    
    ProdLB --> Prod1
    ProdLB --> Prod2
    ProdLB --> Prod3
    Prod1 --> ProdDB
    Prod2 --> ProdDB
    Prod3 --> ProdDB
    Prod1 --> ProdCache
    Prod2 --> ProdCache
    Prod3 --> ProdCache
    CDN --> ProdLB
    Monitor --> Prod1
    Monitor --> Prod2
    Monitor --> Prod3
    
    Git --> CI
    CI --> Registry
    Registry --> Deploy
    Deploy --> Stage
    Deploy --> Prod1
    Deploy --> Prod2
    Deploy --> Prod3
```

## Diagrama de Banco de Dados

```mermaid
erDiagram
    users {
        int id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    profiles {
        int id PK
        string code UK
        string name
        string description
        boolean is_system
        int priority
    }
    
    permissions {
        int id PK
        string code UK
        string name
        string category
        string description
    }
    
    user_profiles {
        int user_id FK
        int profile_id FK
        datetime assigned_at
    }
    
    profile_permissions {
        int profile_id FK
        int permission_id FK
        datetime granted_at
    }
    
    audit_logs {
        int id PK
        int user_id FK
        string action
        string resource_type
        string resource_id
        json old_values
        json new_values
        string ip_address
        string user_agent
        datetime created_at
    }
    
    transactions {
        int id PK
        string code UK
        string name
        string description
        string handler_class
        boolean is_active
        json parameters_schema
    }
    
    transaction_logs {
        int id PK
        int transaction_id FK
        int user_id FK
        json parameters
        json result
        string status
        datetime started_at
        datetime completed_at
    }
    
    users ||--o{ user_profiles : has
    profiles ||--o{ user_profiles : assigned_to
    profiles ||--o{ profile_permissions : grants
    permissions ||--o{ profile_permissions : granted_to
    users ||--o{ audit_logs : performs
    users ||--o{ transaction_logs : executes
    transactions ||--o{ transaction_logs : recorded_for
```

## Diagrama de Sequência - Login Completo

```mermaid
sequenceDiagram
    participant U as Usuário
    participant UI as Interface
    participant AS as Auth Service
    participant DB as Banco de Dados
    participant AL as Audit Logger
    participant RBAC as RBAC System
    
    U->>UI: 1. Insere credenciais
    UI->>AS: 2. Envia login request
    AS->>DB: 3. Busca usuário por username
    DB-->>AS: 4. Retorna user record
    AS->>AS: 5. Verifica password com BCrypt
    AS->>DB: 6. Busca perfis do usuário
    DB-->>AS: 7. Retorna lista de perfis
    AS->>RBAC: 8. Obtém permissões dos perfis
    RBAC-->>AS: 9. Retorna permissões consolidadas
    AS->>AS: 10. Gera token JWT
    AS->>AL: 11. Registra login bem-sucedido
    AL->>DB: 12. Persiste log de auditoria
    AS-->>UI: 13. Retorna token JWT
    UI->>UI: 14. Armazena token localmente
    UI-->>U: 15. Redireciona para dashboard
```

## Diagrama de Monitoramento

```mermaid
graph LR
    subgraph "Application Metrics"
        APM[Application Performance]
        Business[Business Metrics]
        User[User Behavior]
    end
    
    subgraph "Infrastructure Metrics"
        CPU[CPU Usage]
        Memory[Memory Usage]
        Disk[Disk I/O]
        Network[Network Traffic]
    end
    
    subgraph "Security Metrics"
        LoginAttempts[Login Attempts]
        FailedAuth[Failed Auth]
        Suspicious[Suspicious Activity]
        AuditTrail[Audit Trail]
    end
    
    subgraph "Monitoring Tools"
        Prometheus[Prometheus]
        Grafana[Grafana Dashboards]
        AlertManager[Alert Manager]
        ELK[ELK Stack]
    end
    
    APM --> Prometheus
    Business --> Prometheus
    User --> Prometheus
    CPU --> Prometheus
    Memory --> Prometheus
    Disk --> Prometheus
    Network --> Prometheus
    LoginAttempts --> Prometheus
    FailedAuth --> Prometheus
    Suspicious --> Prometheus
    AuditTrail --> ELK
    
    Prometheus --> Grafana
    Prometheus --> AlertManager
    ELK --> Grafana
    
    AlertManager --> Slack[Slack Alerts]
    AlertManager --> Email[Email Notifications]
    AlertManager --> PagerDuty[PagerDuty]
```

## Legenda dos Diagramas

### Símbolos Utilizados
- **Retângulo**: Componente/Processo
- **Círculo**: Banco de Dados/Storage
- **Setas**: Fluxo de dados/controle
- **Subgraph**: Agrupamento lógico
- **Linha Pontilhada**: Dependência opcional

### Cores (quando aplicável)
- **Azul**: Componentes do sistema
- **Verde**: Fluxos bem-sucedidos
- **Vermelho**: Fluxos de erro
- **Amarelo**: Componentes de infraestrutura
- **Roxo**: Componentes de segurança

## Próximos Diagramas

1. [Diagrama de Classes](./02_diagrama_classes.md)
2. [Diagrama de Sequência Detalhado](./03_diagrama_sequencia.md)
3. [Diagrama de Banco de Dados Completo](./04_diagrama_banco_dados.md)

---

**Diagramas Gerados**: 2026-04-14  
**Ferramentas**: Mermaid.js, Draw.io  
**Versão**: 1.0  
**Atualizações Automáticas**: Semanais via CI/CD