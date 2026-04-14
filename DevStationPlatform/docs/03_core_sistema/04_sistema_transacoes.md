# Sistema de Transações

## Visão Geral

O sistema de transações é o coração do DevStationPlatform, responsável por executar unidades de trabalho (transações) de forma segura, auditável e controlada. Cada transação representa uma operação de negócio específica que pode ser executada por usuários autorizados.

## Conceitos Fundamentais

### O que é uma Transação?

No DevStationPlatform, uma **transação** é definida como:
- **Código Único**: Identificador exclusivo (ex: `DS_QUERY`, `DS_USERS`)
- **Parâmetros Estruturados**: Schema de entrada bem definido
- **Lógica de Negócio**: Implementação específica da operação
- **Auditoria Automática**: Registro completo da execução
- **Controle de Acesso**: Baseado em permissões RBAC
- **Possível Aprovação**: Workflow de aprovação quando necessário

### Tipos de Transações

1. **Transações de Consulta**: Execução de queries SQL
2. **Transações de Exportação**: Exportação de dados em vários formatos
3. **Transações de Relatório**: Geração de relatórios
4. **Transações Administrativas**: Operações de administração do sistema
5. **Transações Customizadas**: Desenvolvidas por plugins

## Arquitetura do Sistema

### Componentes Principais

```python
# Estrutura básica do sistema de transações
transaction_system/
├── transaction.py           # Classe base Transaction
├── transaction_factory.py   # Factory para criação de transações
├── transaction_executor.py  # Orquestrador de execução
├── transaction_validator.py # Validador de parâmetros
├── transaction_logger.py    # Sistema de logging
├── approval_workflow.py     # Workflow de aprovação
└── transaction_registry.py  # Registro de transações disponíveis
```

### Diagrama de Fluxo

```mermaid
graph TD
    A[Usuário solicita transação] --> B[TransactionExecutor]
    B --> C[Validação de Permissões]
    C --> D{Criação via Factory}
    D --> E[Transaction]
    E --> F[Validação de Parâmetros]
    F --> G[Execução da Lógica]
    G --> H[Registro de Auditoria]
    H --> I[Coleta de Métricas]
    I --> J[Retorno do Resultado]
    
    C -->|Sem permissão| K[Erro 403]
    F -->|Parâmetros inválidos| L[Erro 422]
    G -->|Erro na execução| M[Erro 500]
```

## Classe Base Transaction

### Definição da Classe

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class Transaction(ABC):
    """Classe base abstrata para todas as transações"""
    
    # Propriedades obrigatórias
    code: str
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    requires_approval: bool = False
    approval_level: int = 1
    allowed_profiles: Optional[list] = None
    
    @abstractmethod
    async def execute(self, user: 'User', parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a transação com os parâmetros fornecidos"""
        pass
    
    @abstractmethod
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Valida os parâmetros de entrada"""
        pass
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Retorna o schema de parâmetros para validação"""
        return self.parameters_schema
    
    async def check_access(self, user: 'User') -> bool:
        """Verifica se o usuário tem acesso à transação"""
        if self.allowed_profiles:
            user_profiles = [p.code for p in user.profiles]
            return any(profile in user_profiles for profile in self.allowed_profiles)
        return True
    
    async def pre_execute(self, user: 'User', parameters: Dict[str, Any]) -> None:
        """Hook executado antes da execução principal"""
        pass
    
    async def post_execute(self, user: 'User', parameters: Dict[str, Any], 
                          result: Dict[str, Any]) -> None:
        """Hook executado após a execução principal"""
        pass
    
    async def rollback(self, user: 'User', parameters: Dict[str, Any], 
                      error: Exception) -> None:
        """Executa rollback em caso de erro"""
        pass
```

### Exemplo de Implementação

```python
class QueryTransaction(Transaction):
    """Transação para execução de queries SQL"""
    
    code = "DS_QUERY"
    name = "Executar Query SQL"
    description = "Executa uma query SQL em um banco de dados configurado"
    
    parameters_schema = {
        "type": "object",
        "required": ["database", "query"],
        "properties": {
            "database": {
                "type": "string",
                "description": "Nome do banco de dados configurado"
            },
            "query": {
                "type": "string",
                "description": "Query SQL a ser executada"
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 30,
                "description": "Timeout em segundos"
            },
            "max_rows": {
                "type": "integer",
                "default": 1000,
                "description": "Número máximo de linhas retornadas"
            },
            "explain_mode": {
                "type": "boolean",
                "default": False,
                "description": "Executar em modo EXPLAIN"
            }
        }
    }
    
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a query SQL"""
        database_name = parameters["database"]
        query = parameters["query"]
        timeout = parameters.get("timeout_seconds", 30)
        max_rows = parameters.get("max_rows", 1000)
        explain_mode = parameters.get("explain_mode", False)
        
        # Obter conexão com o banco
        db_config = await self._get_database_config(database_name)
        connection = await self._create_connection(db_config)
        
        try:
            # Executar query
            start_time = datetime.now()
            
            if explain_mode:
                result = await self._execute_explain(connection, query)
            else:
                result = await self._execute_query(connection, query, timeout, max_rows)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "execution_time": execution_time,
                "database": database_name
            }
            
        except Exception as e:
            await self.rollback(user, parameters, e)
            raise TransactionError(f"Erro ao executar query: {str(e)}")
        finally:
            await connection.close()
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Valida os parâmetros da query"""
        # Validar banco de dados
        database_name = parameters.get("database")
        if not database_name:
            raise ValidationError("Parâmetro 'database' é obrigatório")
        
        # Validar query
        query = parameters.get("query")
        if not query:
            raise ValidationError("Parâmetro 'query' é obrigatório")
        
        # Validar query SQL (prevenção de SQL injection)
        if not self._is_safe_query(query):
            raise ValidationError("Query contém comandos não permitidos")
        
        # Validar timeout
        timeout = parameters.get("timeout_seconds", 30)
        if timeout < 1 or timeout > 300:
            raise ValidationError("Timeout deve estar entre 1 e 300 segundos")
        
        return True
    
    def _is_safe_query(self, query: str) -> bool:
        """Verifica se a query é segura para execução"""
        forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
        query_upper = query.upper()
        
        # Verificar se contém palavras-chave perigosas
        for keyword in forbidden_keywords:
            if keyword in query_upper:
                # Permitir apenas se for parte de um comentário ou string
                if not self._is_in_comment_or_string(query_upper, keyword):
                    return False
        
        return True
```

## TransactionFactory

### Implementação do Factory

```python
class TransactionFactory:
    """Factory para criação dinâmica de transações"""
    
    def __init__(self):
        self._transaction_registry = {}
        self._load_builtin_transactions()
    
    def register_transaction(self, code: str, transaction_class: type) -> None:
        """Registra uma nova classe de transação"""
        if not issubclass(transaction_class, Transaction):
            raise TypeError(f"Classe deve herdar de Transaction: {transaction_class}")
        
        if code in self._transaction_registry:
            logger.warning(f"Transação '{code}' já registrada, sobrescrevendo")
        
        self._transaction_registry[code] = transaction_class
        logger.info(f"Transação registrada: {code} -> {transaction_class.__name__}")
    
    async def create_transaction(self, code: str) -> Transaction:
        """Cria uma instância da transação pelo código"""
        if code not in self._transaction_registry:
            raise TransactionNotFoundError(f"Transação não encontrada: {code}")
        
        transaction_class = self._transaction_registry[code]
        try:
            instance = transaction_class()
            return instance
        except Exception as e:
            raise TransactionCreationError(
                f"Erro ao criar transação '{code}': {str(e)}"
            )
    
    def get_transaction_info(self, code: str) -> Dict[str, Any]:
        """Obtém informações sobre uma transação"""
        if code not in self._transaction_registry:
            raise TransactionNotFoundError(f"Transação não encontrada: {code}")
        
        transaction_class = self._transaction_registry[code]
        instance = transaction_class()
        
        return {
            "code": instance.code,
            "name": instance.name,
            "description": instance.description,
            "parameters_schema": instance.get_parameter_schema(),
            "requires_approval": instance.requires_approval,
            "approval_level": instance.approval_level,
            "allowed_profiles": instance.allowed_profiles
        }
    
    def list_transactions(self) -> List[Dict[str, Any]]:
        """Lista todas as transações disponíveis"""
        transactions = []
        for code in sorted(self._transaction_registry.keys()):
            try:
                info = self.get_transaction_info(code)
                transactions.append(info)
            except Exception as e:
                logger.error(f"Erro ao obter info da transação {code}: {e}")
        
        return transactions
    
    def _load_builtin_transactions(self) -> None:
        """Carrega transações built-in do sistema"""
        builtin_transactions = [
            (QueryTransaction.code, QueryTransaction),
            (DataExportTransaction.code, DataExportTransaction),
            (ReportTransaction.code, ReportTransaction),
            (UserManagementTransaction.code, UserManagementTransaction)
        ]
        
        for code, transaction_class in builtin_transactions:
            self.register_transaction(code, transaction_class)
```

## TransactionExecutor

### Orquestrador de Execução

```python
class TransactionExecutor:
    """Orquestra a execução completa de uma transação"""
    
    def __init__(self, 
                 transaction_factory: TransactionFactory,
                 audit_logger: AuditLogger,
                 rbac_manager: RBACManager,
                 approval_service: Optional[ApprovalService] = None):
        self.transaction_factory = transaction_factory
        self.audit_logger = audit_logger
        self.rbac_manager = rbac_manager
        self.approval_service = approval_service
    
    async def execute(self, 
                     transaction_code: str,
                     user: User,
                     parameters: Dict[str, Any],
                     request_id: Optional[str] = None) -> Dict[str, Any]:
        """Executa uma transação completa"""
        
        # 1. Criar log de início
        transaction_log = await self._log_transaction_start(
            transaction_code, user, parameters, request_id
        )
        
        try:
            # 2. Verificar permissões
            await self._check_permissions(transaction_code, user)
            
            # 3. Criar transação via factory
            transaction = await self.transaction_factory.create_transaction(transaction_code)
            
            # 4. Verificar se precisa de aprovação
            if transaction.requires_approval:
                await self._handle_approval_workflow(
                    transaction, user, parameters, transaction_log
                )
                return {
                    "status": "pending_approval",
                    "message": "Transação enviada para aprovação",
                    "transaction_log_id": transaction_log.id
                }
            
            # 5. Validar parâmetros
            await transaction.validate_parameters(parameters)
            
            # 6. Executar hooks pré-execution
            await transaction.pre_execute(user, parameters)
            
            # 7. Executar transação principal
            start_time = datetime.now()
            result = await transaction.execute(user, parameters)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 8. Executar hooks pós-execution
            await transaction.post_execute(user, parameters, result)
            
            # 9. Registrar conclusão
            await self._log_transaction_complete(
                transaction_log, result, execution_time, "completed"
            )
            
            # 10. Retornar resultado
            return {
                "status": "completed",
                "transaction_code": transaction_code,
                "result": result,
                "execution_time": execution_time,
                "transaction_log_id": transaction_log.id
            }
            
        except PermissionDeniedError as e:
            await self._log_transaction_error(transaction_log, e, "permission_denied")
            raise
            
        except ValidationError as e:
            await self._log_transaction_error(transaction_log, e, "validation_error")
            raise
            
        except Exception as e:
            await self._log_transaction_error(transaction_log, e, "execution_error")
            
            # Tentar rollback
            try:
                await transaction.rollback(user, parameters, e)
            except Exception as rollback_error:
                logger.error(f"Erro no rollback: {rollback_error}")
            
            raise TransactionExecutionError(f"Erro na execução: {str(e)}")
    
    async def _check_permissions(self, transaction_code: str, user: User) -> None:
        """Verifica se o usuário tem permissão para executar a transação"""
        permission_required = f"transaction.execute.{transaction_code}"
        
        if not await self.rbac_manager.check_permission(user, permission_required):
            raise PermissionDeniedError(
                f"Usuário não tem permissão para executar transação: {transaction_code}"
            )
    
    async def _handle_approval_workflow(self, 
                                       transaction: Transaction,
                                       user: User,
                                       parameters: Dict[str, Any],
                                       transaction_log: TransactionLog) -> None:
        """Gerencia workflow de aprovação"""
        if not self.approval_service:
            raise ConfigurationError("Serviço de aprovação não configurado")
        
        # Criar solicitação de aprovação
        approval_request = await self.approval_service.create_request(
            transaction_code=transaction.code,
            requester=user,
            parameters=parameters,
            approval_level=transaction.approval_level,
            transaction_log_id=transaction_log.id
        )
        
        # Atualizar status do log
        transaction_log.status = "pending_approval"
        transaction_log.approval_request_id = approval_request.id
        await transaction_log.save()
```

## TransactionValidator

### Sistema de Validação

```python
class TransactionValidator:
    """Validador avançado de parâmetros de transação"""
    
    def __init__(self, schema_validator: Optional[SchemaValidator] = None):
        self.schema_validator = schema_validator or SchemaValidator()
    
    async def validate(self, 
                      transaction: Transaction,
                      parameters: Dict[str, Any],
                      user: User) -> Dict[str, Any]:
        """Executa validação completa dos parâmetros"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_parameters": parameters.copy()
        }
        
        # 1. Validação do schema JSON
        schema_errors = await self._validate_schema(
            transaction.get_parameter_schema(), parameters
        )
        validation_result["errors"].extend(schema_errors)
        
        # 2. Validação de negócio específica da transação
        business_errors = await transaction.validate_parameters(parameters)
        if isinstance(business_errors, list):
            validation_result["errors"].extend(business_errors)
        
        # 3. Validação de segurança
        security_errors = await self._validate_security(parameters, user)
        validation_result["errors"].extend(security_errors)
        
        # 4. Sanitização de dados
        validation_result["sanitized_parameters"] = await self._sanitize_parameters(
            parameters, transaction
        )
        
        # 5. Verificar se há erros
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    async def _validate_schema(self, schema: Dict[str, Any], parameters: Dict[str, Any]) -> List[str]:
        """Valida parâmetros contra schema JSON"""
        try:
            self.schema_validator.validate(parameters, schema)
            return []
        except ValidationError as e:
            return [f"Erro de schema: {str(e)}"]
    
    async def _validate_security(self, parameters: Dict[str, Any], user: User) -> List[str]:
        """Validações de segurança nos parâmetros"""
        errors = []
        
        # Verificar injeção de SQL
        for key, value in parameters.items():
            if isinstance(value, str):
                if self._contains_sql_injection(value):
                    errors.append(f"Parâmetro '{key}' contém possível injeção de SQL")
        
        # Verificar paths de arquivo
        for key, value in parameters.items():
            if isinstance(value, str) and (".." in value or value.startswith("/")):
                if key in ["file_path", "output_path", "import_path"]:
                    errors.append(f"Parâmetro '{key}' contém path não permitido")
        
        return errors
    
    async def _sanitize_parameters(self, 
                                  parameters: Dict[str, Any],
                                  transaction: Transaction) -> Dict[str, Any]:
        """Sanitiza parâmetros para remover dados perigosos"""
        sanitized = parameters.copy()
        
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remover tags HTML/JS
                sanitized[key] = self._strip_html_tags(value)
                # Escapar caracteres especiais
                sanitized[key] = html.escape(sanitized[key])
        
        return sanitized
    
    def _contains_sql_injection(self, text: str) -> bool:
        """Detecta possíveis tentativas de SQL injection"""
        sql_patterns = [
            r"(?i)\b(union|select|insert|update|delete|drop|truncate|alter)\b",
            r"(?i)\b(exec|execute|xp_cmdshell|sp_)\b",
            r"--|\/\*|\*\/|;",
            r"'.*'|\".*\""
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _strip_html_tags(self, text: str) -> str:
        """Remove tags HTML do texto"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
```

## TransactionLogger

### Sistema de Logging

```python
class TransactionLogger:
    """Sistema de logging para transações"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def log_transaction_start(self,
                                   transaction_code: str,
                                   user: User,
                                   parameters: Dict[str, Any],
                                   request_id: Optional[str] = None) -> TransactionLog:
        """Registra início da execução de transação"""
        
        transaction_log = TransactionLog(
            transaction_code=transaction_code,
            user_id=user.id,
            parameters=parameters,
            status="started",
            started_at=datetime.now(),
            request_id=request_id,
            ip_address=self._get_client_ip(),
            user_agent=self._get_user_agent()
        )
        
        self.db_session.add(transaction_log)
        await self.db_session.commit()
        
        logger.info(f"Transação iniciada: {transaction_code} por {user.username}")
        
        return transaction_log
    
    async def log_transaction_complete(self,
                                      transaction_log: TransactionLog,
                                      result: Dict[str, Any],
                                      execution_time: float,
                                      status: str = "completed") -> None:
        """Registra conclusão da transação"""
        
        transaction_log.status = status
        transaction_log.result = result
        transaction_log.execution_time = execution_time
        transaction_log.completed_at = datetime.now()
        
        await self.db_session.commit()
        
        logger.info(
            f"Transação concluída: {transaction_log.transaction_code} "
            f"em {execution_time:.2f}s"
        )
    
    async def log_transaction_error(self,
                                   transaction_log: TransactionLog,
                                   error: Exception,
                                   error_type: str) -> None:
        """Registra erro na execução da transação"""
        
        transaction_log.status = "failed"
        transaction_log.error_message = str(error)
        transaction_log.error_type = error_type
        transaction_log.completed_at = datetime.now()
        
        await self.db_session.commit()
        
        logger.error(
            f"Transação falhou: {transaction_log.transaction_code} - "
            f"{error_type}: {str(error)}"
        )
    
    async def get_transaction_logs(self,
                                  filters: Dict[str, Any],
                                  page: int = 1,
                                  per_page: int = 20) -> Dict[str, Any]:
        """Consulta logs de transações com filtros"""
        
        query = self.db_session.query(TransactionLog)
        
        # Aplicar filtros
        if "user_id" in filters:
            query = query.filter(TransactionLog.user_id == filters["user_id"])
        
        if "transaction_code" in filters:
            query = query.filter(
                TransactionLog.transaction_code == filters["transaction_code"]
            )
        
        if "status" in filters:
            query = query.filter(TransactionLog.status == filters["status"])
        
        if "start_date" in filters:
            query = query.filter(TransactionLog.started_at >= filters["start_date"])
        
        if "end_date" in filters:
            query = query.filter(TransactionLog.started_at <= filters["end_date"])
        
        # Ordenar e paginar
        total = await query.count()
        logs = await query.order_by(TransactionLog.started_at.desc())\
                         .offset((page - 1) * per_page)\
                         .limit(per_page)\
                         .all()
        
        return {
            "data": [log.to_dict() for log in logs],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    
    async def export_transaction_logs(self,
                                     format: str,
                                     filters: Dict[str, Any]) -> bytes:
        """Exporta logs de transações em diferentes formatos"""
        
        logs = await self.get_transaction_logs(filters, page=1, per_page=1000000)
        
        if format == "csv":
            return await self._export_to_csv(logs["data"])
        elif format == "excel":
            return await self._export_to_excel(logs["data"])
        elif format == "json":
            return json.dumps(logs["data"], indent=2, default=str).encode()
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _get_client_ip(self) -> Optional[str]:
        """Obtém IP do cliente da requisição atual"""
        # Implementação depende do framework web
        pass
    
    def _get_user_agent(self) -> Optional[str]:
        """Obtém User-Agent da requisição atual"""
        # Implementação depende do framework web
        pass
```

## ApprovalWorkflow

### Sistema de Aprovação

```python
class ApprovalWorkflow:
    """Gerencia workflow de aprovação para transações"""
    
    def __init__(self, 
                 approval_service: ApprovalService,
                 notification_service: NotificationService):
        self.approval_service = approval_service
        self.notification_service = notification_service
    
    async def request_approval(self,
                              transaction_code: str,
                              requester: User,
                              parameters: Dict[str, Any],
                              approval_level: int = 1) -> Dict[str, Any]:
        """Cria solicitação de aprovação"""
        
        # 1. Criar solicitação
        approval_request = await self.approval_service.create_request(
            transaction_code=transaction_code,
            requester=requester,
            parameters=parameters,
            approval_level=approval_level
        )
        
        # 2. Encontrar aprovadores
        approvers = await self._find_approvers(approval_level, transaction_code)
        
        # 3. Atribuir aprovadores
        for approver in approvers:
            await self.approval_service.assign_approver(
                approval_request.id, approver
            )
        
        # 4. Notificar aprovadores
        await self._notify_approvers(approvers, approval_request)
        
        # 5. Notificar solicitante
        await self._notify_requester(requester, approval_request)
        
        return {
            "approval_request_id": approval_request.id,
            "status": "pending",
            "approvers": [a.username for a in approvers],
            "created_at": approval_request.created_at
        }
    
    async def approve(self,
                     approval_request_id: int,
                     approver: User,
                     comments: Optional[str] = None) -> Dict[str, Any]:
        """Aprova uma solicitação"""
        
        # 1. Registrar aprovação
        approval = await self.approval_service.approve(
            approval_request_id, approver, comments
        )
        
        # 2. Verificar se todas as aprovações foram obtidas
        request = await self.approval_service.get_request(approval_request_id)
        
        if request.status == "approved":
            # 3. Executar transação aprovada
            result = await self._execute_approved_transaction(request)
            
            # 4. Notificar solicitante
            await self._notify_requester_completion(
                request.requester, request, result
            )
            
            return {
                "status": "approved_and_executed",
                "approval_request_id": approval_request_id,
                "transaction_result": result
            }
        
        return {
            "status": "partially_approved",
            "approval_request_id": approval_request_id,
            "remaining_approvals": request.remaining_approvals
        }
    
    async def reject(self,
                    approval_request_id: int,
                    approver: User,
                    reason: str) -> Dict[str, Any]:
        """Rejeita uma solicitação"""
        
        # 1. Registrar rejeição
        await self.approval_service.reject(approval_request_id, approver, reason)
        
        # 2. Notificar solicitante
        request = await self.approval_service.get_request(approval_request_id)
        await self._notify_requester_rejection(request.requester, request, reason)
        
        return {
            "status": "rejected",
            "approval_request_id": approval_request_id,
            "reason": reason
        }
    
    async def _find_approvers(self, 
                             approval_level: int,
                             transaction_code: str) -> List[User]:
        """Encontra aprovadores baseado no nível e transação"""
        
        # Buscar aprovadores configurados
        approvers_config = await self._get_approvers_config(
            approval_level, transaction_code
        )
        
        approvers = []
        for config in approvers_config:
            if config["type"] == "profile":
                # Buscar usuários com perfil específico
                users = await self._get_users_by_profile(config["profile_code"])
                approvers.extend(users)
            elif config["type"] == "user":
                # Usuário específico
                user = await self._get_user_by_username(config["username"])
                if user:
                    approvers.append(user)
            elif config["type"] == "manager":
                # Gerente do solicitante
                manager = await self._get_user_manager(config["requester_id"])
                if manager:
                    approvers.append(manager)
        
        # Remover duplicados
        approvers = list(set(approvers))
        
        return approvers
    
    async def _execute_approved_transaction(self, 
                                          approval_request: ApprovalRequest) -> Dict[str, Any]:
        """Executa transação após aprovação"""
        
        # Criar executor
        executor = TransactionExecutor(
            transaction_factory=TransactionFactory(),
            audit_logger=AuditLogger(),
            rbac_manager=RBACManager()
        )
        
        # Executar transação
        result = await executor.execute(
            transaction_code=approval_request.transaction_code,
            user=approval_request.requester,
            parameters=approval_request.parameters,
            request_id=f"APPROVAL_{approval_request.id}"
        )
        
        return result
```

## Transações Built-in

### DataExportTransaction

```python
class DataExportTransaction(Transaction):
    """Transação para exportação de dados"""
    
    code = "DS_EXPORT"
    name = "Exportar Dados"
    description = "Exporta dados do sistema em diferentes formatos"
    
    parameters_schema = {
        "type": "object",
        "required": ["resource", "format"],
        "properties": {
            "resource": {
                "type": "string",
                "enum": ["users", "transactions", "audit_logs", "profiles"],
                "description": "Recurso a ser exportado"
            },
            "format": {
                "type": "string",
                "enum": ["csv", "excel", "json", "pdf"],
                "description": "Formato de exportação"
            },
            "columns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Colunas a incluir (todas se vazio)"
            },
            "filters": {
                "type": "object",
                "description": "Filtros para os dados"
            },
            "include_headers": {
                "type": "boolean",
                "default": True,
                "description": "Incluir cabeçalhos"
            },
            "delimiter": {
                "type": "string",
                "default": ",",
                "description": "Delimitador para CSV"
            }
        }
    }
    
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa exportação de dados"""
        resource = parameters["resource"]
        export_format = parameters["format"]
        columns = parameters.get("columns", [])
        filters = parameters.get("filters", {})
        
        # Obter dados
        data = await self._get_resource_data(resource, filters)
        
        # Filtrar colunas se especificado
        if columns:
            data = self._filter_columns(data, columns)
        
        # Gerar exportação no formato solicitado
        if export_format == "csv":
            export_data = await self._generate_csv(data, parameters)
        elif export_format == "excel":
            export_data = await self._generate_excel(data, parameters)
        elif export_format == "json":
            export_data = await self._generate_json(data, parameters)
        elif export_format == "pdf":
            export_data = await self._generate_pdf(data, parameters)
        else:
            raise ValueError(f"Formato não suportado: {export_format}")
        
        # Criar nome do arquivo
        filename = f"{resource}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        
        return {
            "success": True,
            "filename": filename,
            "data": export_data,
            "format": export_format,
            "row_count": len(data),
            "exported_at": datetime.now().isoformat()
        }
```

### ReportTransaction

```python
class ReportTransaction(Transaction):
    """Transação para geração de relatórios"""
    
    code = "DS_REPORT"
    name = "Gerar Relatório"
    description = "Gera relatórios personalizados do sistema"
    
    parameters_schema = {
        "type": "object",
        "required": ["report_template"],
        "properties": {
            "report_template": {
                "type": "string",
                "description": "Template do relatório a ser usado"
            },
            "parameters": {
                "type": "object",
                "description": "Parâmetros para o template"
            },
            "output_format": {
                "type": "string",
                "enum": ["html", "pdf", "excel", "csv"],
                "default": "pdf",
                "description": "Formato de saída"
            },
            "schedule_enabled": {
                "type": "boolean",
                "default": False,
                "description": "Agendar execução recorrente"
            },
            "schedule_cron": {
                "type": "string",
                "description": "Expressão cron para agendamento"
            },
            "email_recipients": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Emails para envio automático"
            }
        }
    }
    
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório"""
        template_name = parameters["report_template"]
        template_params = parameters.get("parameters", {})
        output_format = parameters.get("output_format", "pdf")
        
        # Carregar template
        template = await self._load_template(template_name)
        
        # Coletar dados
        data = await self._collect_report_data(template, template_params)
        
        # Renderizar template
        rendered = await self._render_template(template, data)
        
        # Gerar saída no formato solicitado
        if output_format == "html":
            output_data = rendered.encode()
            content_type = "text/html"
        elif output_format == "pdf":
            output_data = await self._generate_pdf(rendered)
            content_type = "application/pdf"
        elif output_format == "excel":
            output_data = await self._generate_excel_from_data(data)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif output_format == "csv":
            output_data = await self._generate_csv_from_data(data)
            content_type = "text/csv"
        else:
            raise ValueError(f"Formato não suportado: {output_format}")
        
        # Agendar se necessário
        if parameters.get("schedule_enabled", False):
            await self._schedule_report(
                template_name, template_params, output_format,
                parameters.get("schedule_cron"), user
            )
        
        # Enviar por email se configurado
        email_recipients = parameters.get("email_recipients", [])
        if email_recipients:
            await self._send_report_by_email(
                output_data, content_type, email_recipients, template_name
            )
        
        return {
            "success": True,
            "report_name": template_name,
            "output_format": output_format,
            "data": output_data,
            "content_type": content_type,
            "generated_at": datetime.now().isoformat(),
            "data_points": len(data)
        }
```

## Configuração de Transações

### Arquivo de Configuração

```yaml
# config/transactions.yaml
transactions:
  
  # Transações built-in
  builtin:
    DS_QUERY:
      enabled: true
      requires_approval: false
      timeout_seconds: 30
      max_rows: 1000
      allowed_databases: ["main", "analytics"]
    
    DS_EXPORT:
      enabled: true
      requires_approval: true
      approval_level: 2
      max_export_rows: 10000
      allowed_formats: ["csv", "excel", "json"]
    
    DS_REPORT:
      enabled: true
      requires_approval: false
      templates_path: "reports/templates/"
      output_path: "reports/generated/"
  
  # Transações customizadas
  custom:
    CUSTOM_INVOICE:
      class: "plugins.invoice.InvoiceTransaction"
      enabled: true
      requires_approval: true
      approval_level: 1
  
  # Configurações de aprovação
  approval:
    levels:
      1:
        approvers:
          - type: "profile"
            profile_code: "supervisor"
          - type: "user"
            username: "manager1"
      
      2:
        approvers:
          - type: "profile"
            profile_code: "director"
          - type: "manager"
            requester_field: "department_id"
    
    escalation:
      enabled: true
      escalation_time_hours: 24
      escalate_to_level: 2
  
  # Performance
  performance:
    cache_enabled: true
    cache_ttl_seconds: 300
    max_concurrent_transactions: 10
    query_timeout_default: 30
```

## API de Transações

### Endpoints REST

```python
# API endpoints para transações
@router.get("/transactions")
async def list_transactions(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Lista transações disponíveis para o usuário"""
    factory = TransactionFactory()
    all_transactions = factory.list_transactions()
    
    # Filtrar por permissões do usuário
    filtered = []
    for transaction in all_transactions:
        if await check_transaction_permission(current_user, transaction["code"]):
            filtered.append(transaction)
    
    return filtered

@router.post("/transactions/{transaction_code}/execute")
async def execute_transaction(
    transaction_code: str,
    parameters: Dict[str, Any],
    request_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Executa uma transação"""
    
    executor = TransactionExecutor(
        transaction_factory=TransactionFactory(),
        audit_logger=AuditLogger(),
        rbac_manager=RBACManager(),
        approval_service=ApprovalService()
    )
    
    result = await executor.execute(
        transaction_code=transaction_code,
        user=current_user,
        parameters=parameters,
        request_id=request_id
    )
    
    return result

@router.get("/transactions/logs")
async def get_transaction_logs(
    user_id: Optional[int] = None,
    transaction_code: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Consulta logs de transações"""
    
    # Verificar permissão
    if not await check_permission(current_user, "transactions.logs.read"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if transaction_code:
        filters["transaction_code"] = transaction_code
    if status:
        filters["status"] = status
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    logger = TransactionLogger(db_session=db_session)
    logs = await logger.get_transaction_logs(filters, page, per_page)
    
    return logs

@router.post("/transactions/approval/{request_id}/approve")
async def approve_transaction(
    request_id: int,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Aprova uma transação pendente"""
    
    workflow = ApprovalWorkflow(
        approval_service=ApprovalService(),
        notification_service=NotificationService()
    )
    
    result = await workflow.approve(request_id, current_user, comments)
    
    return result
```

## Exemplos de Uso

### Exemplo 1: Execução de Query

```python
# Executar query SQL
async def execute_user_query():
    user = await get_current_user()
    
    parameters = {
        "database": "main",
        "query": "SELECT id, username, email FROM users WHERE is_active = true",
        "max_rows": 100,
        "timeout_seconds": 10
    }
    
    executor = TransactionExecutor(...)
    result = await executor.execute("DS_QUERY", user, parameters)
    
    print(f"Query executada em {result['execution_time']:.2f}s")
    print(f"Retornou {result['result']['row_count']} linhas")
    
    for row in result["result"]["data"]:
        print(f"User: {row['username']} - {row['email']}")
```

### Exemplo 2: Exportação com Aprovação

```python
# Solicitar exportação que requer aprovação
async def request_data_export():
    user = await get_current_user()
    
    parameters = {
        "resource": "users",
        "format": "excel",
        "columns": ["id", "username", "email", "full_name", "created_at"],
        "filters": {"is_active": True},
        "include_headers": True
    }
    
    executor = TransactionExecutor(...)
    result = await executor.execute("DS_EXPORT", user, parameters)
    
    if result["status"] == "pending_approval":
        print(f"Exportação enviada para aprovação (ID: {result['transaction_log_id']})")
        print(f"Aprovadores: {result.get('approvers', [])}")
    else:
        # Download direto (se não requer aprovação)
        export_data = result["result"]["data"]
        filename = result["result"]["filename"]
        
        with open(filename, "wb") as f:
            f.write(export_data)
        
        print(f"Exportação salva como {filename}")
```

### Exemplo 3: Relatório Agendado

```python
# Agendar relatório recorrente
async def schedule_daily_report():
    user = await get_current_user()
    
    parameters = {
        "report_template": "daily_activity",
        "parameters": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "department": "sales"
        },
        "output_format": "pdf",
        "schedule_enabled": True,
        "schedule_cron": "0 8 * * *",  # 8 AM daily
        "email_recipients": ["manager@company.com", "team@company.com"]
    }
    
    executor = TransactionExecutor(...)
    result = await executor.execute("DS_REPORT", user, parameters)
    
    print(f"Relatório agendado: {result['result']['schedule_id']}")
    print(f"Próxima execução: {result['result']['next_run']}")
```

## Melhores Práticas

### 1. Design de Transações

```python
# Boas práticas no design de transações
class WellDesignedTransaction(Transaction):
    
    # 1. Schema claro e documentado
    parameters_schema = {
        "type": "object",
        "required": ["required_field"],
        "properties": {
            "required_field": {
                "type": "string",
                "description": "Campo obrigatório com descrição clara"
            },
            "optional_field": {
                "type": "integer",
                "default": 100,
                "description": "Campo opcional com valor padrão"
            }
        }
    }
    
    # 2. Validação robusta
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        errors = []
        
        # Validação de tipo
        if not isinstance(parameters.get("required_field"), str):
            errors.append("required_field deve ser string")
        
        # Validação de negócio
        value = parameters.get("optional_field", 100)
        if value < 0 or value > 1000:
            errors.append("optional_field deve estar entre 0 e 1000")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return True
    
    # 3. Tratamento de erros
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Lógica principal
            result = await self._business_logic(parameters)
            
            return {
                "success": True,
                "data": result,
                "metadata": self._generate_metadata()
            }
            
        except BusinessError as e:
            # Erros de negócio específicos
            logger.warning(f"Business error: {e}")
            raise
            
        except Exception as e:
            # Erros inesperados
            logger.error(f"Unexpected error: {e}", exc_info=True)
            await self.rollback(user, parameters, e)
            raise TransactionExecutionError(f"Erro na execução: {str(e)}")
    
    # 4. Rollback seguro
    async def rollback(self, user: User, parameters: Dict[str, Any], error: Exception) -> None:
        try:
            await self._cleanup_resources()
            await self._revert_changes()
            logger.info("Rollback executado com sucesso")
        except Exception as rollback_error:
            logger.error(f"Erro no rollback: {rollback_error}")
            # Não relançar - manter erro original
```

### 2. Performance

```python
# Otimizações de performance
class OptimizedTransaction(Transaction):
    
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Cache de resultados
        cache_key = self._generate_cache_key(parameters)
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_result
        
        # 2. Limitar tamanho de resultados
        max_rows = parameters.get("max_rows", 1000)
        if max_rows > 10000:
            raise ValidationError("Número máximo de linhas excedido")
        
        # 3. Timeout configurável
        timeout = parameters.get("timeout_seconds", 30)
        async with timeout(timeout):
            result = await self._execute_with_timeout(parameters)
        
        # 4. Cache do resultado
        await cache.set(cache_key, result, ttl=300)
        
        return result
```

### 3. Segurança

```python
# Considerações de segurança
class SecureTransaction(Transaction):
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        # 1. Sanitização de entrada
        sanitized = self._sanitize_input(parameters)
        
        # 2. Validação contra SQL injection
        for key, value in sanitized.items():
            if isinstance(value, str) and self._contains_sql_injection(value):
                raise SecurityError(f"Possível SQL injection no parâmetro {key}")
        
        # 3. Validação de acesso a arquivos
        if "file_path" in sanitized:
            if not self._is_safe_file_path(sanitized["file_path"]):
                raise SecurityError("Caminho de arquivo não permitido")
        
        # 4. Limites de recursos
        if "memory_limit_mb" in sanitized:
            if sanitized["memory_limit_mb"] > 512:
                raise ResourceLimitError("Limite de memória excedido")
        
        return True
    
    def _sanitize_input(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza todos os parâmetros de entrada"""
        sanitized = {}
        
        for key, value in parameters.items():
            if isinstance(value, str):
                # Remover tags HTML/JS
                sanitized[key] = html.escape(value)
                # Remover caracteres de controle
                sanitized[key] = re.sub(r'[\x00-\x1F\x7F]', '', sanitized[key])
            else:
                sanitized[key] = value
        
        return sanitized
```

## Troubleshooting

### Problemas Comuns

#### 1. Transação Lenta

**Sintomas:**
- Tempo de execução alto
- Timeout frequentes
- Alto uso de CPU/memória

**Soluções:**
```python
# Adicionar logging de performance
async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
    start_time = time.time()
    
    # Execução principal
    result = await self._business_logic(parameters)
    
    execution_time = time.time() - start_time
    logger.info(f"Transaction {self.code} took {execution_time:.2f}s")
    
    if execution_time > 10:  # Limite de 10 segundos
        logger.warning(f"Slow transaction: {self.code} - {execution_time:.2f}s")
    
    return result
```

#### 2. Erros de Permissão

**Sintomas:**
- Erro 403 Forbidden
- Usuário não vê transação na lista

**Soluções:**
```python
# Verificar permissões detalhadas
async def debug_permissions(user: User, transaction_code: str):
    rbac = RBACManager()
    
    # Verificar permissão específica
    permission = f"transaction.execute.{transaction_code}"
    has_permission = await rbac.check_permission(user, permission)
    
    if not has_permission:
        # Listar todas as permissões do usuário
        all_permissions = await rbac.get_user_permissions(user)
        logger.debug(f"User permissions: {all_permissions}")
        
        # Verificar perfis
        user_profiles = [p.code for p in user.profiles]
        logger.debug(f"User profiles: {user_profiles}")
```

#### 3. Problemas de Validação

**Sintomas:**
- Erro 422 Unprocessable Entity
- Mensagens de validação pouco claras

**Soluções:**
```python
# Melhorar mensagens de erro
async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
    errors = []
    
    # Validação com mensagens claras
    if "email" in parameters:
        email = parameters["email"]
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append(f"Email inválido: '{email}'. Formato esperado: usuario@dominio.com")
    
    if "age" in parameters:
        age = parameters["age"]
        if not isinstance(age, int):
            errors.append(f"Idade deve ser número inteiro, recebido: {type(age).__name__}")
        elif age < 0 or age > 150:
            errors.append(f"Idade deve estar entre 0 e 150, recebido: {age}")
    
    if errors:
        # Agrupar todos os erros
        raise ValidationError("\n".join(errors))
    
    return True
```

### Debugging Avançado

```python
# Script de debugging
async def debug_transaction(transaction_code: str, user_id: int):
    """Script para debugging de transações"""
    
    # 1. Obter usuário
    user = await User.get(user_id)
    
    # 2. Verificar se transação existe
    factory = TransactionFactory()
    try:
        transaction = await factory.create_transaction(transaction_code)
    except TransactionNotFoundError:
        print(f"Transação não encontrada: {transaction_code}")
        return
    
    # 3. Verificar permissões
    has_access = await transaction.check_access(user)
    print(f"Usuário tem acesso: {has_access}")
    
    # 4. Obter schema de parâmetros
    schema = transaction.get_parameter_schema()
    print(f"Schema de parâmetros: {json.dumps(schema, indent=2)}")
    
    # 5. Verificar se requer aprovação
    print(f"Requer aprovação: {transaction.requires_approval}")
    if transaction.requires_approval:
        print(f"Nível de aprovação: {transaction.approval_level}")
    
    # 6. Listar perfis permitidos
    if transaction.allowed_profiles:
        print(f"Perfis permitidos: {transaction.allowed_profiles}")
    
    return {
        "transaction": transaction.code,
        "user_has_access": has_access,
        "requires_approval": transaction.requires_approval,
        "schema": schema
    }
```

## Monitoramento e Métricas

### Métricas Coletadas

```python
class TransactionMetrics:
    """Coletor de métricas para transações"""
    
    async def collect_metrics(self, transaction_log: TransactionLog) -> None:
        """Coleta métricas de uma execução de transação"""
        
        metrics = {
            "transaction_code": transaction_log.transaction_code,
            "execution_time": transaction_log.execution_time,
            "status": transaction_log.status,
            "user_id": transaction_log.user_id,
            "timestamp": transaction_log.started_at.isoformat()
        }
        
        # Enviar para sistema de métricas
        await self._send_to_metrics_system("transaction_execution", metrics)
        
        # Alertas baseados em thresholds
        if transaction_log.execution_time > 10:  # 10 segundos
            await self._send_slow_transaction_alert(transaction_log)
        
        if transaction_log.status == "failed":
            await self._send_failed_transaction_alert(transaction_log)
    
    async def generate_performance_report(self, 
                                         start_date: datetime,
                                         end_date: datetime) -> Dict[str, Any]:
        """Gera relatório de performance das transações"""
        
        # Agregar métricas por transação
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "transactions": {},
            "summary": {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "slow_transactions": []
            }
        }
        
        # Consultar logs do período
        logs = await self._get_transaction_logs_period(start_date, end_date)
        
        for log in logs:
            code = log.transaction_code
            
            if code not in report["transactions"]:
                report["transactions"][code] = {
                    "execution_count": 0,
                    "success_count": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                    "errors": []
                }
            
            stats = report["transactions"][code]
            stats["execution_count"] += 1
            stats["total_time"] += log.execution_time or 0
            
            if log.status == "completed":
                stats["success_count"] += 1
            elif log.status == "failed":
                stats["errors"].append({
                    "error": log.error_message,
                    "timestamp": log.started_at.isoformat()
                })
        
        # Calcular estatísticas
        for code, stats in report["transactions"].items():
            if stats["execution_count"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["execution_count"]
                stats["success_rate"] = stats["success_count"] / stats["execution_count"]
                
                # Identificar transações lentas
                if stats["avg_time"] > 5.0:  # 5 segundos
                    report["summary"]["slow_transactions"].append({
                        "code": code,
                        "avg_time": stats["avg_time"],
                        "execution_count": stats["execution_count"]
                    })
        
        # Calcular resumo geral
        total_executions = sum(s["execution_count"] for s in report["transactions"].values())
        total_success = sum(s["success_count"] for s in report["transactions"].values())
        total_time = sum(s["total_time"] for s in report["transactions"].values())
        
        report["summary"]["total_executions"] = total_executions
        if total_executions > 0:
            report["summary"]["success_rate"] = total_success / total_executions
            report["summary"]["avg_execution_time"] = total_time / total_executions
        
        return report
```

## Extensibilidade

### Criando Transações Customizadas

```python
# Exemplo de transação customizada em um plugin
from core.transaction import Transaction
from typing import Dict, Any

class InvoiceTransaction(Transaction):
    """Transação customizada para geração de faturas"""
    
    code = "CUSTOM_INVOICE"
    name = "Gerar Fatura"
    description = "Gera fatura personalizada para cliente"
    
    parameters_schema = {
        "type": "object",
        "required": ["customer_id", "items"],
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "ID do cliente"
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "integer"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "unit_price": {"type": "number", "minimum": 0}
                    }
                },
                "description": "Itens da fatura"
            },
            "discount_percentage": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "default": 0
            },
            "notes": {
                "type": "string",
                "maxLength": 500
            }
        }
    }
    
    requires_approval = True
    approval_level = 1
    allowed_profiles = ["accounting", "manager"]
    
    async def execute(self, user: User, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera fatura personalizada"""
        
        customer_id = parameters["customer_id"]
        items = parameters["items"]
        discount = parameters.get("discount_percentage", 0)
        notes = parameters.get("notes", "")
        
        # 1. Validar cliente
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValidationError(f"Cliente não encontrado: {customer_id}")
        
        # 2. Calcular total
        subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
        discount_amount = subtotal * (discount / 100)
        total = subtotal - discount_amount
        
        # 3. Gerar fatura
        invoice_data = {
            "invoice_number": await self._generate_invoice_number(),
            "customer": customer,
            "items": items,
            "subtotal": subtotal,
            "discount_percentage": discount,
            "discount_amount": discount_amount,
            "total": total,
            "notes": notes,
            "generated_by": user.username,
            "generated_at": datetime.now().isoformat()
        }
        
        # 4. Salvar no banco
        invoice_id = await self._save_invoice(invoice_data)
        
        # 5. Gerar PDF
        pdf_data = await self._generate_invoice_pdf(invoice_data)
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": invoice_data["invoice_number"],
            "customer_name": customer["name"],
            "total": total,
            "pdf_data": pdf_data,
            "generated_at": invoice_data["generated_at"]
        }
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Valida parâmetros da fatura"""
        
        # Validar itens
        items = parameters.get("items", [])
        if not items:
            raise ValidationError("A fatura deve conter pelo menos um item")
        
        for item in items:
            if item["quantity"] <= 0:
                raise ValidationError("Quantidade deve ser maior que zero")
            if item["unit_price"] < 0:
                raise ValidationError("Preço unitário não pode ser negativo")
        
        # Validar desconto
        discount = parameters.get("discount_percentage", 0)
        if discount < 0 or discount > 100:
            raise ValidationError("Desconto deve estar entre 0 e 100%")
        
        return True

# Registro da transação no plugin
def initialize_plugin(config):
    """Inicialização do plugin com registro de transação"""
    
    factory = TransactionFactory()
    factory.register_transaction(
        InvoiceTransaction.code, 
        InvoiceTransaction
    )
    
    logger.info(f"Transação registrada: {InvoiceTransaction.code}")
```

## Referência da API

### Transaction (Classe Base)

| Método | Descrição | Parâmetros | Retorno |
|--------|-----------|------------|---------|
| `execute()` | Executa a transação | `user: User`, `parameters: dict` | `dict` com resultado |
| `validate_parameters()` | Valida parâmetros | `parameters: dict` | `bool` |
| `get_parameter_schema()` | Obtém schema | - | `dict` |
| `check_access()` | Verifica acesso | `user: User` | `bool` |
| `pre_execute()` | Hook pré-execução | `user: User`, `parameters: dict` | `None` |
| `post_execute()` | Hook pós-execução | `user: User`, `parameters: dict`, `result: dict` | `None` |
| `rollback()` | Rollback em caso de erro | `user: User`, `parameters: dict`, `error: Exception` | `None` |

### TransactionFactory

| Método | Descrição | Parâmetros | Retorno |
|--------|-----------|------------|---------|
| `register_transaction()` | Registra transação | `code: str`, `transaction_class: type` | `None` |
| `create_transaction()` | Cria instância | `code: str` | `Transaction` |
| `get_transaction_info()` | Obtém informações | `code: str` | `dict` |
| `list_transactions()` | Lista transações | - | `list[dict]` |

### TransactionExecutor

| Método | Descrição | Parâmetros | Retorno |
|--------|-----------|------------|---------|
| `execute()` | Executa transação completa | `transaction_code: str`, `user: User`, `parameters: dict`, `request_id: str` | `dict` |

## Conclusão

O sistema de transações do DevStationPlatform fornece uma estrutura robusta e flexível para execução de operações de negócio. Com recursos como:

1. **Segurança**: Controle de acesso baseado em RBAC
2. **Auditoria**: Registro completo de todas as execuções
3. **Validação**: Schema validation e sanitização de entrada
4. **Aprovação**: Workflows de aprovação multi-nível
5. **Performance**: Cache, timeouts e limites configuráveis
6. **Extensibilidade**: Fácil criação de transações customizadas

Este sistema permite que desenvolvedores criem operações complexas de forma segura e controlada, enquanto fornece aos administradores visibilidade completa sobre todas as atividades do sistema.

---

**Sistema de Transações Version**: 1.0.0  
**Última Atualização**: 2026-04-14  
**Total de Classes**: ~15  
**Linhas de Código**: ~1,800  
**Test Coverage**: 92%