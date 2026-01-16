"""
Sistema de autenticação e grupos de usuários.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import db


class UserGroup(db.Model):
    """Grupos de usuários do sistema."""
    __tablename__ = 'user_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # Grupos do sistema não podem ser deletados
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    users = relationship('User', back_populates='group')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<UserGroup {self.name}>'


class User(UserMixin, db.Model):
    """Modelo de usuário para autenticação."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey('user_groups.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Campos de perfil
    nome = Column(String(120))
    nome_completo = Column(String(255))
    empresa = Column(String(255))
    cargo = Column(String(255))
    telefone = Column(String(50))
    foto_perfil = Column(String(255))
    
    # Relacionamentos
    group = relationship('UserGroup', back_populates='users')
    
    def set_password(self, password):
        """Define a senha do usuário."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def password(self):
        raise AttributeError("password is write-only")
    
    @password.setter
    def password(self, password: str):
        self.set_password(password)
    
    def verify_password(self, password: str) -> bool:
        return self.check_password(password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'group_id': self.group_id,
            'group': self.group.to_dict() if self.group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'nome': self.nome,
            'nome_completo': self.nome_completo,
            'empresa': self.empresa,
            'cargo': self.cargo,
            'telefone': self.telefone,
            'foto_perfil': self.foto_perfil,
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def initialize_default_groups():
        """Inicializa os grupos padrão do sistema."""
        groups = [
            {'name': 'Administrador', 'description': 'Acesso total ao sistema', 'is_system': True},
            {'name': 'Auditor', 'description': 'Pode aprovar/rejeitar alterações via Excel', 'is_system': True},
            {'name': 'Operador', 'description': 'Pode fazer uploads mas não aprovar', 'is_system': True},
            {'name': 'Visualizador', 'description': 'Apenas visualização de dados', 'is_system': True},
        ]
        
        for group_data in groups:
            existing = UserGroup.query.filter_by(name=group_data['name']).first()
            if not existing:
                group = UserGroup(**group_data)
                db.session.add(group)
        
        db.session.commit()
