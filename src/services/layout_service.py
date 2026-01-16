"""
Serviço para gerenciamento de layouts.
"""

from db.database import db
from model.layout import Layout
from model.table_config import TableConfig
from flask_login import current_user


class LayoutService:
    """Serviço para operações com layouts."""
    
    @staticmethod
    def get_active_layout(table_config_id: int, user_id: int = None, group_id: int = None) -> Layout:
        """
        Obtém o layout ativo para uma tabela seguindo a hierarquia:
        pessoal > grupo > padrão
        
        Args:
            table_config_id: ID da configuração da tabela
            user_id: ID do usuário (opcional)
            group_id: ID do grupo (opcional)
        
        Returns:
            Layout ativo ou None
        """
        # 1. Tentar layout pessoal
        if user_id:
            personal_layout = Layout.query.filter_by(
                table_config_id=table_config_id,
                user_id=user_id,
                group_id=None
            ).first()
            if personal_layout:
                return personal_layout
        
        # 2. Tentar layout de grupo
        if group_id:
            group_layout = Layout.query.filter_by(
                table_config_id=table_config_id,
                user_id=None,
                group_id=group_id
            ).first()
            if group_layout:
                return group_layout
        
        # 3. Tentar layout padrão
        default_layout = Layout.query.filter_by(
            table_config_id=table_config_id,
            user_id=None,
            group_id=None,
            is_default=True
        ).first()
        
        return default_layout
    
    @staticmethod
    def save_layout(table_config_id: int, name: str, description: str = None,
                    visible_fields: list = None, filters: dict = None,
                    order_by: str = None, order_dir: str = 'asc', per_page: int = 20,
                    group_by: list = None, summarize_fields: dict = None,
                    user_id: int = None, group_id: int = None, is_default: bool = False) -> Layout:
        """
        Salva um layout.
        
        Args:
            table_config_id: ID da configuração da tabela
            name: Nome do layout
            description: Descrição
            visible_fields: Lista de campos visíveis
            filters: Filtros aplicados
            order_by: Campo de ordenação
            order_dir: Direção da ordenação
            per_page: Registros por página
            group_by: Campos para agrupar
            summarize_fields: Campos para sumarizar
            user_id: ID do usuário (para layout pessoal)
            group_id: ID do grupo (para layout de grupo)
            is_default: Se é layout padrão
        
        Returns:
            Layout salvo
        """
        # Se é layout padrão, remover outros padrões
        if is_default:
            Layout.query.filter_by(
                table_config_id=table_config_id,
                is_default=True
            ).update({'is_default': False})
        
        layout = Layout(
            table_config_id=table_config_id,
            user_id=user_id,
            group_id=group_id,
            name=name,
            description=description,
            is_default=is_default,
            visible_fields=visible_fields or [],
            filters=filters or {},
            order_by=order_by,
            order_dir=order_dir,
            per_page=per_page,
            group_by=group_by or [],
            summarize_fields=summarize_fields or {}
        )
        
        db.session.add(layout)
        db.session.commit()
        
        return layout
    
    @staticmethod
    def update_layout(layout_id: int, **kwargs) -> Layout:
        """
        Atualiza um layout existente.
        
        Args:
            layout_id: ID do layout
            **kwargs: Campos a atualizar
        
        Returns:
            Layout atualizado
        """
        layout = Layout.query.get_or_404(layout_id)
        
        for key, value in kwargs.items():
            if hasattr(layout, key):
                setattr(layout, key, value)
        
        db.session.commit()
        
        return layout
    
    @staticmethod
    def delete_layout(layout_id: int):
        """Remove um layout."""
        layout = Layout.query.get_or_404(layout_id)
        db.session.delete(layout)
        db.session.commit()
    
    @staticmethod
    def list_layouts(table_config_id: int, user_id: int = None) -> list:
        """
        Lista layouts disponíveis para uma tabela.
        
        Args:
            table_config_id: ID da configuração da tabela
            user_id: ID do usuário (para filtrar layouts pessoais)
        
        Returns:
            Lista de layouts
        """
        query = Layout.query.filter_by(table_config_id=table_config_id)
        
        if user_id:
            # Incluir layouts pessoais, de grupo e padrões
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Layout.user_id == user_id,
                    Layout.user_id.is_(None)
                )
            )
        
        layouts = query.order_by(Layout.is_default.desc(), Layout.name).all()
        
        return [layout.to_dict() for layout in layouts]
