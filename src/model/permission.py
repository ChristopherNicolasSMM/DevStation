"""
Modelo de permissões granular do sistema.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from db.database import db


class PermissionType(enum.Enum):
    """Tipos de permissão."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VISIBLE = "VISIBLE"  # Para campos
    EDITABLE = "EDITABLE"  # Para campos


class PermissionTarget(enum.Enum):
    """Alvo da permissão."""
    TABLE = "TABLE"
    FIELD = "FIELD"


class Permission(db.Model):
    """Permissão granular do sistema."""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Alvo da permissão (tabela ou campo)
    target_type = Column(Enum(PermissionTarget), nullable=False)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    field_name = Column(String(100), nullable=True)  # None para permissão de tabela, nome do campo para permissão de campo
    
    # Tipo de permissão
    permission_type = Column(Enum(PermissionType), nullable=False)
    
    # Usuário ou grupo
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    group_id = Column(Integer, ForeignKey('user_groups.id', ondelete='CASCADE'), nullable=True)
    
    # Relacionamentos
    user = relationship('User', foreign_keys=[user_id])
    group = relationship('UserGroup', foreign_keys=[group_id])
    table_config = relationship('TableConfig')
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type.value if self.target_type else None,
            'table_config_id': self.table_config_id,
            'field_name': self.field_name,
            'permission_type': self.permission_type.value if self.permission_type else None,
            'user_id': self.user_id,
            'group_id': self.group_id,
        }
    
    def __repr__(self):
        target = f"{self.table_config_id}" + (f".{self.field_name}" if self.field_name else "")
        user_group = f"user:{self.user_id}" if self.user_id else f"group:{self.group_id}"
        return f'<Permission {self.permission_type.value} on {target} for {user_group}>'
    
    @staticmethod
    def grant_table_permission(user_id=None, group_id=None, table_config_id=None, permission_type=None):
        """Concede permissão de tabela."""
        if not table_config_id or not permission_type:
            raise ValueError("table_config_id e permission_type são obrigatórios")
        
        if not user_id and not group_id:
            raise ValueError("user_id ou group_id deve ser fornecido")
        
        permission = Permission(
            target_type=PermissionTarget.TABLE,
            table_config_id=table_config_id,
            permission_type=permission_type,
            user_id=user_id,
            group_id=group_id
        )
        db.session.add(permission)
        db.session.commit()
        return permission
    
    @staticmethod
    def grant_field_permission(user_id=None, group_id=None, table_config_id=None, field_name=None, permission_type=None):
        """Concede permissão de campo."""
        if not table_config_id or not field_name or not permission_type:
            raise ValueError("table_config_id, field_name e permission_type são obrigatórios")
        
        if not user_id and not group_id:
            raise ValueError("user_id ou group_id deve ser fornecido")
        
        permission = Permission(
            target_type=PermissionTarget.FIELD,
            table_config_id=table_config_id,
            field_name=field_name,
            permission_type=permission_type,
            user_id=user_id,
            group_id=group_id
        )
        db.session.add(permission)
        db.session.commit()
        return permission
