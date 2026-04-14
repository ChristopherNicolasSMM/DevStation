# Diagrama de Classes

## Visão Geral das Classes

Este diagrama mostra as principais classes do sistema e seus relacionamentos.

## Diagrama de Classes Principal

```mermaid
classDiagram
    %% Core Base Classes
    class BaseModel {
        +int id
        +datetime created_at
        +datetime updated_at
        +save()
        +delete()
        +to_dict()
    }
    
    class Config {
        +dict settings
        +str environment
        +load_config()
        +get(key)
        +set(key, value)
    }
    
    class AuditLogger {
        +log_action()
        +log_transaction()
        +get_logs()
        +export_logs()
    }
    
    %% Security Classes
    class AuthService {
        +authenticate(username, password)
        +generate_token(user)
        +validate_token(token)
        +logout(token)
    }
    
    class RBACManager {
        +check_permission(user, permission)
        +get_user_permissions(user)
        +assign_profile(user, profile)
        +revoke_profile(user, profile)
    }
    
    class ProfileManager {
        +create_profile(data)
        +update_profile(profile_id, data)
        +delete_profile(profile_id)
        +get_profile_permissions(profile)
    }
    
    %% Transaction Classes
    class Transaction {
        +str code
        +str name
        +str description
        +dict parameters_schema
        +execute(user, parameters)
        +validate_parameters(parameters)
    }
    
    class TransactionHandler {
        +Transaction transaction
        +handle(user, parameters)
        +pre_execute()
        +post_execute()
        +rollback()
    }
    
    class TransactionFactory {
        +create_transaction(code)
        +register_handler(code, handler_class)
        +get_available_transactions()
    }
    
    %% Plugin Classes
    class BasePlugin {
        +str name
        +str version
        +str description
        +initialize()
        +register_routes()
        +cleanup()
    }
    
    class PluginManager {
        +list plugins
        +load_plugin(path)
        +unload_plugin(plugin)
        +get_plugin(name)
        +reload_plugins()
    }
    
    %% UI Classes
    class BaseView {
        +str route
        +str name
        +list permissions
        +render()
        +handle_request()
        +validate_access()
    }
    
    class MenuManager {
        +dict menu_structure
        +get_user_menu(user)
        +add_menu_item(item)
        +remove_menu_item(route)
    }
    
    class ThemeManager {
        +str current_theme
        +dict themes
        +set_theme(theme_name)
        +get_theme_css()
        +register_theme(theme)
    }
    
    %% Database Models
    class User {
        +str username
        +str email
        +str password_hash
        +str full_name
        +bool is_active
        +list profiles
        +check_password(password)
        +change_password(new_password)
    }
    
    class Profile {
        +str code
        +str name
        +str description
        +bool is_system
        +int priority
        +list permissions
        +list parent_profiles
    }
    
    class Permission {
        +str code
        +str name
        +str category
        +str description
    }
    
    class AuditLog {
        +User user
        +str action
        +str resource_type
        +str resource_id
        +dict old_values
        +dict new_values
        +str ip_address
        +str user_agent
    }
    
    class TransactionLog {
        +Transaction transaction
        +User user
        +dict parameters
        +dict result
        +str status
        +datetime started_at
        +datetime completed_at
    }
    
    %% Relationships
    BaseModel <|-- User
    BaseModel <|-- Profile
    BaseModel <|-- Permission
    BaseModel <|-- AuditLog
    BaseModel <|-- TransactionLog
    
    User "1" -- "*" Profile : has
    Profile "*" -- "*" Permission : grants
    Profile "*" -- "*" Profile : inherits from
    
    User "1" -- "*" AuditLog : performs
    User "1" -- "*" TransactionLog : executes
    
    Transaction "1" -- "*" TransactionLog : recorded in
    
    AuthService --> User : authenticates
    RBACManager --> User : checks permissions
    RBACManager --> Profile : manages
    RBACManager --> Permission : validates
    
    TransactionFactory --> Transaction : creates
    TransactionHandler --> Transaction : handles
    
    PluginManager --> BasePlugin : manages
    BaseView --> RBACManager : checks access
    
    MenuManager --> BaseView : organizes
    ThemeManager --> BaseView : styles
```

## Diagrama de Classes Detalhado - Módulo de Segurança

```mermaid
classDiagram
    class User {
        +str username
        +str email
        +str password_hash
        +str full_name
        +bool is_active
        +datetime last_login
        +int failed_attempts
        +bool locked
        +check_password(password) bool
        +change_password(old_pass, new_pass) bool
        +lock_account()
        +unlock_account()
        +increment_failed_attempts()
        +reset_failed_attempts()
    }
    
    class Profile {
        +str code
        +str name
        +str description
        +bool is_system
        +int priority
        +datetime created_at
        +User created_by
        +add_permission(permission)
        +remove_permission(permission)
        +has_permission(permission_code) bool
        +get_all_permissions() list
        +add_parent_profile(profile)
        +remove_parent_profile(profile)
    }
    
    class Permission {
        +str code
        +str name
        +str category
        +str description
        +bool is_system
        +validate_action(action) bool
    }
    
    class UserProfile {
        +User user
        +Profile profile
        +datetime assigned_at
        +User assigned_by
        +datetime expires_at
        +bool is_active
    }
    
    class ProfilePermission {
        +Profile profile
        +Permission permission
        +datetime granted_at
        +User granted_by
        +datetime expires_at
    }
    
    class ProfileInheritance {
        +Profile child_profile
        +Profile parent_profile
        +datetime inherited_at
    }
    
    class AuthService {
        -str jwt_secret
        -int jwt_expiry_hours
        +authenticate(username, password) dict
        +generate_token(user) str
        +validate_token(token) dict
        +refresh_token(token) str
        +logout(token) bool
        +validate_password_strength(password) bool
    }
    
    class RBACService {
        +check_permission(user, permission_code) bool
        +get_user_permissions(user) list
        +has_any_permission(user, permissions) bool
        +has_all_permissions(user, permissions) bool
        +filter_by_permission(users, permission) list
    }
    
    class PasswordService {
        +hash_password(password) str
        +verify_password(password, hash) bool
        +generate_temp_password() str
        +validate_password_policy(password) dict
    }
    
    class SessionManager {
        +dict active_sessions
        +create_session(user, ip, user_agent) str
        +validate_session(session_id) bool
        +end_session(session_id)
        +cleanup_expired_sessions()
        +get_user_sessions(user) list
    }
    
    %% Relationships
    User "1" -- "*" UserProfile : "assigned to"
    Profile "1" -- "*" UserProfile : "assigned from"
    
    Profile "1" -- "*" ProfilePermission : "grants"
    Permission "1" -- "*" ProfilePermission : "granted to"
    
    Profile "1" -- "*" ProfileInheritance : "child of"
    Profile "1" -- "*" ProfileInheritance : "parent of"
    
    AuthService --> User : "authenticates"
    AuthService --> PasswordService : "uses"
    
    RBACService --> User : "checks permissions"
    RBACService --> Profile : "traverses hierarchy"
    RBACService --> Permission : "validates"
    
    SessionManager --> User : "manages sessions"
```

## Diagrama de Classes - Sistema de Transações

```mermaid
classDiagram
    class Transaction {
        <<abstract>>
        +str code
        +str name
        +str description
        +dict parameters_schema
        +bool requires_approval
        +int approval_level
        +list allowed_profiles
        +execute(user, parameters) dict
        +validate_parameters(parameters) bool
        +get_parameter_schema() dict
        +check_access(user) bool
    }
    
    class QueryTransaction {
        +str database
        +str query
        +int timeout_seconds
        +int max_rows
        +bool explain_mode
        +execute(user, parameters) dict
        +validate_query(query) bool
        +sanitize_input(input) str
    }
    
    class DataExportTransaction {
        +str format
        +list columns
        +dict filters
        +bool include_headers
        +str delimiter
        +execute(user, parameters) dict
        +generate_csv(data) bytes
        +generate_excel(data) bytes
        +generate_pdf(data) bytes
    }
    
    class ReportTransaction {
        +str report_template
        +dict parameters
        +str output_format
        +bool schedule_enabled
        +str schedule_cron
        +execute(user, parameters) dict
        +render_template(data) str
        +generate_output(html, format) bytes
    }
    
    class TransactionFactory {
        -dict transaction_registry
        +register_transaction(code, transaction_class)
        +create_transaction(code) Transaction
        +get_transaction_info(code) dict
        +list_transactions() list
        +validate_transaction_code(code) bool
    }
    
    class TransactionExecutor {
        +Transaction transaction
        +User user
        +dict parameters
        +execute() dict
        +validate() bool
        +log_start()
        +log_complete(result)
        +log_error(error)
        +rollback() bool
    }
    
    class TransactionValidator {
        +Transaction transaction
        +dict parameters
        +validate() dict
        +validate_required_fields() list
        +validate_data_types() list
        +validate_business_rules() list
        +get_validation_schema() dict
    }
    
    class TransactionLogger {
        +log_transaction_start(transaction, user)
        +log_transaction_complete(transaction_log, result)
        +log_transaction_error(transaction_log, error)
        +get_transaction_logs(filters) list
        +export_transaction_logs(format, filters) bytes
    }
    
    class ApprovalWorkflow {
        +Transaction transaction
        +User requester
        +dict parameters
        +list approvers
        +int current_level
        +str status
        +request_approval()
        +approve(approver, comments)
        +reject(approver, reason)
        +get_approval_history() list
        +escalate()
    }
    
    %% Relationships
    Transaction <|-- QueryTransaction
    Transaction <|-- DataExportTransaction
    Transaction <|-- ReportTransaction
    
    TransactionFactory --> Transaction : creates
    
    TransactionExecutor --> Transaction : executes
    TransactionExecutor --> TransactionValidator : validates
    TransactionExecutor --> TransactionLogger : logs
    
    TransactionValidator --> Transaction : validates
    
    ApprovalWorkflow --> Transaction : manages approval
    ApprovalWorkflow --> User : involves approvers
```

## Diagrama de Classes - Sistema de Plugins

```mermaid
classDiagram
    class BasePlugin {
        <<abstract>>
        +str name
        +str version
        +str description
        +str author
        +list dependencies
        +dict metadata
        +initialize(config) bool
        +register_routes(app)
        +register_events()
        +register_commands()
        +cleanup()
        +get_status() dict
    }
    
    class UIPlugin {
        +list ui_components
        +dict menu_items
        +dict routes
        +register_ui_components()
        +add_menu_item(item)
        +add_route(path, component)
    }
    
    class DataPlugin {
        +list data_sources
        +dict data_models
        +dict data_processors
        +register_data_models()
        +add_data_source(name, config)
        +process_data(source, processor)
    }
    
    class IntegrationPlugin {
        +list external_apis
        +dict webhook_endpoints
        +dict event_listeners
        +register_integrations()
        +call_api(api_name, method, data)
        +handle_webhook(endpoint, data)
    }
    
    class PluginManager {
        -dict loaded_plugins
        -list plugin_paths
        +load_plugin(path) BasePlugin
        +unload_plugin(plugin_name) bool
        +reload_plugin(plugin_name) bool
        +get_plugin(plugin_name) BasePlugin
        +list_plugins() list
        +check_dependencies(plugin) bool
        +resolve_conflicts(plugin1, plugin2) dict
    }
    
    class PluginLoader {
        +load_from_path(path) BasePlugin
        +load_from_package(package_name) BasePlugin
        +validate_plugin_structure(plugin_dir) bool
        +check_requirements(requirements) bool
        +install_dependencies(dependencies) bool
    }
    
    class PluginRegistry {
        -dict plugin_registry
        +register_plugin(plugin)
        +unregister_plugin(plugin_name)
        +find_plugin_by_feature(feature) list
        +get_plugin_dependencies(plugin_name) list
        +check_plugin_compatibility(plugin1, plugin2) bool
    }
    
    class PluginHookSystem {
        -dict hooks
        +register_hook(hook_name, callback)
        +trigger_hook(hook_name, *args, **kwargs)
        +get_hook_listeners(hook_name) list
        +remove_hook(hook_name, callback)
    }
    
    %% Relationships
    BasePlugin <|-- UIPlugin
    BasePlugin <|-- DataPlugin
    BasePlugin <|-- IntegrationPlugin
    
    PluginManager --> PluginLoader : uses
    PluginManager --> PluginRegistry : manages
    PluginManager --> PluginHookSystem : integrates
    
    PluginLoader --> BasePlugin : loads
    
    PluginRegistry --> BasePlugin : registers
    
    PluginHookSystem --> BasePlugin : provides hooks
```

## Diagrama de Classes - Sistema de Auditoria

```mermaid
classDiagram
    class AuditLogger {
        +log_action(user, action, resource, old_val, new_val)
        +log_security_event(user, event_type, details)
        +log_system_event(event_type, details)
        +log_performance_metric(metric_name, value)
        +get_audit_trail(filters) list
        +export_audit_logs(format, filters) bytes
        +cleanup_old_logs(retention_days)
    }
    
    class AuditLog {
        +int id
        +User user
        +str action
        +str resource_type
        +str resource_id
        +json old_values
        +json new_values
        +str ip_address
        +str user_agent
        +datetime timestamp
        +str session_id
        +get_changes_summary() str
        +to_dict() dict
    }
    
    class SecurityEvent {
        +str event_type
        +str severity
        +dict details
        +str source_ip
        +str target_resource
        +bool blocked
        +str response_action
        +datetime detected_at
        +analyze_threat_level() str
        +generate_alert() dict
    }
    
    class PerformanceMetric {
        +str metric_name
        +float value
        +str unit
        +dict tags
        +datetime timestamp
        +str source
        +bool is_anomaly
        +calculate_trend() float
        +check_threshold() bool
    }
    
    class AuditConfig {
        +bool enabled
        +list logged_actions
        +list excluded_actions
        +int retention_days
        +bool log_ip_address
        +bool log_user_agent
        +bool real_time_alerts
        +list alert_recipients
        +validate_config() bool
        +update_config(new_config)
    }
    
    class AuditExporter {
        +export_to_csv(logs) bytes
        +export_to_excel(logs) bytes
        +export_to_pdf(logs) bytes
        +export_to_json(logs) bytes
        +generate_report(logs, template) bytes
        +compress_data(data, format) bytes
    }
    
    class AuditAnalyzer {
        +list logs
        +analyze_user_behavior(user) dict
        +detect_anomalies(time_range) list
        +generate_compliance_report() dict
        +calculate_metrics(metric_name, period) dict
        +find_correlation(event1, event2) float
    }
    
    class AlertManager {
        +list active_alerts
        +dict alert_rules
        +check_alerts(log_entry)
        +send_alert(alert, recipients)
        +escalate_alert(alert)
        +resolve_alert(alert_id)
        +get_alert_history() list
    }
    
    %% Relationships
    AuditLogger --> AuditLog : creates
    AuditLogger --> SecurityEvent : logs
    AuditLogger --> PerformanceMetric : records
    
    AuditLogger --> AuditConfig : uses configuration
    
    AuditExporter --> AuditLog : exports
    AuditExporter --> SecurityEvent : exports
    AuditExporter --> PerformanceMetric : exports
    
    AuditAnalyzer --> AuditLog : analyzes
    AuditAnalyzer --> SecurityEvent : analyzes
    AuditAnalyzer --> PerformanceMetric : analyzes
    
    AlertManager --> SecurityEvent : manages alerts
   