"""
Serviço para verificação e gerenciamento de permissões.
"""

from functools import wraps
from flask import abort, jsonify
from flask_login import current_user
from db.database import db
from model.permission import Permission, PermissionType, PermissionTarget
from model.user import User, UserGroup


class PermissionService:
    """Serviço para operações com permissões."""
    
    @staticmethod
    def has_table_permission(user, table_config_id, permission_type: PermissionType):
        """
        Verifica se o usuário tem permissão na tabela.
        
        Args:
            user: Instância de User
            table_config_id: ID da configuração da tabela
            permission_type: Tipo de permissão (CREATE, READ, UPDATE, DELETE)
        
        Returns:
            True se tem permissão, False caso contrário
        """
        # Administradores têm todas as permissões
        if user.is_admin:
            return True
        
        # Verificar permissões do usuário
        user_permission = Permission.query.filter_by(
            target_type=PermissionTarget.TABLE,
            table_config_id=table_config_id,
            permission_type=permission_type,
            user_id=user.id
        ).first()
        
        if user_permission:
            return True
        
        # Verificar permissões do grupo
        if user.group_id:
            group_permission = Permission.query.filter_by(
                target_type=PermissionTarget.TABLE,
                table_config_id=table_config_id,
                permission_type=permission_type,
                group_id=user.group_id
            ).first()
            
            if group_permission:
                return True
        
        return False
    
    @staticmethod
    def has_field_permission(user, table_config_id, field_name, permission_type: PermissionType):
        """
        Verifica se o usuário tem permissão no campo.
        
        Args:
            user: Instância de User
            table_config_id: ID da configuração da tabela
            field_name: Nome do campo
            permission_type: Tipo de permissão (VISIBLE, EDITABLE)
        
        Returns:
            True se tem permissão, False caso contrário
        """
        # Administradores têm todas as permissões
        if user.is_admin:
            return True
        
        # Verificar permissões do usuário
        user_permission = Permission.query.filter_by(
            target_type=PermissionTarget.FIELD,
            table_config_id=table_config_id,
            field_name=field_name,
            permission_type=permission_type,
            user_id=user.id
        ).first()
        
        if user_permission:
            return True
        
        # Verificar permissões do grupo
        if user.group_id:
            group_permission = Permission.query.filter_by(
                target_type=PermissionTarget.FIELD,
                table_config_id=table_config_id,
                field_name=field_name,
                permission_type=permission_type,
                group_id=user.group_id
            ).first()
            
            if group_permission:
                return True
        
        return False
    
    @staticmethod
    def get_visible_fields(user, table_config):
        """
        Retorna lista de campos visíveis para o usuário.
        
        Args:
            user: Instância de User
            table_config: Instância de TableConfig
        
        Returns:
            Lista de FieldConfig visíveis
        """
        if user.is_admin:
            return table_config.fields
        
        visible_fields = []
        for field in table_config.fields:
            if PermissionService.has_field_permission(
                user, table_config.id, field.name, PermissionType.VISIBLE
            ):
                visible_fields.append(field)
        
        return visible_fields
    
    @staticmethod
    def get_editable_fields(user, table_config):
        """
        Retorna lista de campos editáveis para o usuário.
        
        Args:
            user: Instância de User
            table_config: Instância de TableConfig
        
        Returns:
            Lista de FieldConfig editáveis
        """
        if user.is_admin:
            return table_config.fields
        
        editable_fields = []
        for field in table_config.fields:
            if PermissionService.has_field_permission(
                user, table_config.id, field.name, PermissionType.EDITABLE
            ):
                editable_fields.append(field)
        
        return editable_fields
    
    @staticmethod
    def check_table_permission(permission_type: PermissionType):
        """
        Decorator para verificar permissão de tabela.
        
        Args:
            permission_type: Tipo de permissão requerida
        
        Usage:
            @permission_service.check_table_permission(PermissionType.READ)
            def my_view(table_id):
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(401)
                
                # Obter table_config_id dos argumentos
                table_config_id = kwargs.get('table_config_id') or kwargs.get('id')
                if not table_config_id:
                    # Tentar obter do request
                    from flask import request
                    table_config_id = request.args.get('table_config_id') or request.json.get('table_config_id') if request.is_json else None
                
                if not table_config_id:
                    abort(400, "table_config_id não fornecido")
                
                if not PermissionService.has_table_permission(
                    current_user, table_config_id, permission_type
                ):
                    abort(403, "Permissão negada")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


def require_table_permission(permission_type: PermissionType):
    """
    Decorator simplificado para verificar permissão de tabela.
    
    Usage:
        @require_table_permission(PermissionType.READ)
        def my_view(table_config_id):
            ...
    """
    return PermissionService.check_table_permission(permission_type)
