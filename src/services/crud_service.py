"""
Serviço CRUD genérico para tabelas dinâmicas.
"""

from sqlalchemy import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError
from db.database import db
from model.table_config import TableConfig
from model.field_config import FieldConfig
from services.table_service import TableService
from services.permission_service import PermissionService
from services.permission_service import PermissionType
from flask_login import current_user


class CRUDService:
    """Serviço para operações CRUD genéricas."""
    
    @staticmethod
    def list_records(table_config_id, page=1, per_page=20, filters=None, order_by=None, order_dir='asc'):
        """
        Lista registros de uma tabela dinâmica.
        
        Args:
            table_config_id: ID da configuração da tabela
            page: Número da página
            per_page: Registros por página
            filters: Dicionário de filtros {field_name: value}
            order_by: Campo para ordenação
            order_dir: Direção da ordenação (asc/desc)
        
        Returns:
            Tupla (registros, total, página, por_página)
        """
        # Verificar permissão de leitura
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.READ
        ):
            raise PermissionError("Sem permissão para ler esta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        
        if not TableService.table_exists(table_config.table_name):
            return [], 0, page, per_page
        
        # Obter modelo dinâmico
        model_class = TableService.get_table_model(table_config)
        if not model_class:
            return [], 0, page, per_page
        
        # Obter campos visíveis
        visible_fields = PermissionService.get_visible_fields(current_user, table_config)
        visible_field_names = [f.name for f in visible_fields]
        
        # Construir query base
        query = db.session.query(model_class)
        
        # Aplicar filtros
        if filters:
            query = CRUDService._apply_filters(query, model_class, table_config, filters, visible_field_names)
        
        # Aplicar ordenação
        if order_by and order_by in visible_field_names:
            order_field = getattr(model_class, order_by)
            if order_dir.lower() == 'desc':
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
        else:
            # Ordenar por ID por padrão
            query = query.order_by(model_class.id.desc())
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação
        records = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Converter para dicionários (apenas campos visíveis)
        records_dict = []
        for record in records:
            record_dict = {'id': record.id}
            for field in visible_fields:
                value = getattr(record, field.name, None)
                record_dict[field.name] = value
            records_dict.append(record_dict)
        
        return records_dict, total, page, per_page
    
    @staticmethod
    def _apply_filters(query, model_class, table_config, filters, visible_field_names):
        """Aplica filtros à query."""
        conditions = []
        
        for field_name, value in filters.items():
            if field_name not in visible_field_names:
                continue
            
            if value is None or value == '':
                continue
            
            # Obter configuração do campo
            field_config = next((f for f in table_config.fields if f.name == field_name), None)
            if not field_config:
                continue
            
            field_attr = getattr(model_class, field_name, None)
            if not field_attr:
                continue
            
            # Aplicar filtro baseado no tipo
            if field_config.field_type == 'text':
                conditions.append(field_attr.ilike(f'%{value}%'))
            elif field_config.field_type in ['number', 'integer']:
                try:
                    conditions.append(field_attr == float(value))
                except ValueError:
                    pass
            elif field_config.field_type == 'date':
                conditions.append(field_attr == value)
            elif field_config.field_type == 'boolean':
                conditions.append(field_attr == (value.lower() in ['true', '1', 'yes']))
            else:
                conditions.append(field_attr == value)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query
    
    @staticmethod
    def get_record(table_config_id, record_id):
        """
        Obtém um registro específico.
        
        Args:
            table_config_id: ID da configuração da tabela
            record_id: ID do registro
        
        Returns:
            Dicionário com os dados do registro
        """
        # Verificar permissão de leitura
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.READ
        ):
            raise PermissionError("Sem permissão para ler esta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        model_class = TableService.get_table_model(table_config)
        
        if not model_class:
            raise ValueError("Tabela não existe no banco")
        
        record = db.session.get(model_class, record_id)
        if not record:
            raise ValueError("Registro não encontrado")
        
        # Obter campos visíveis
        visible_fields = PermissionService.get_visible_fields(current_user, table_config)
        
        # Converter para dicionário
        record_dict = {'id': record.id}
        for field in visible_fields:
            value = getattr(record, field.name, None)
            record_dict[field.name] = value
        
        return record_dict
    
    @staticmethod
    def create_record(table_config_id, data):
        """
        Cria um novo registro.
        
        Args:
            table_config_id: ID da configuração da tabela
            data: Dicionário com os dados do registro
        
        Returns:
            Dicionário com o registro criado
        """
        # Verificar permissão de criação
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.CREATE
        ):
            raise PermissionError("Sem permissão para criar registros nesta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        model_class = TableService.get_table_model(table_config)
        
        if not model_class:
            raise ValueError("Tabela não existe no banco")
        
        # Validar dados
        CRUDService._validate_data(table_config, data, is_update=False)
        
        # Obter campos editáveis
        editable_fields = PermissionService.get_editable_fields(current_user, table_config)
        editable_field_names = [f.name for f in editable_fields]
        
        # Criar instância do modelo
        record = model_class()
        
        # Preencher campos editáveis
        for field in editable_fields:
            if field.name in data:
                value = data[field.name]
                # Converter valor se necessário
                value = CRUDService._convert_value(field, value)
                setattr(record, field.name, value)
            elif field.default_value:
                setattr(record, field.name, field.default_value)
        
        try:
            db.session.add(record)
            db.session.commit()
            
            # Retornar registro criado
            return CRUDService.get_record(table_config_id, record.id)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar registro: {str(e)}")
    
    @staticmethod
    def update_record(table_config_id, record_id, data):
        """
        Atualiza um registro existente.
        
        Args:
            table_config_id: ID da configuração da tabela
            record_id: ID do registro
            data: Dicionário com os dados a atualizar
        
        Returns:
            Dicionário com o registro atualizado
        """
        # Verificar permissão de atualização
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.UPDATE
        ):
            raise PermissionError("Sem permissão para atualizar registros nesta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        model_class = TableService.get_table_model(table_config)
        
        if not model_class:
            raise ValueError("Tabela não existe no banco")
        
        record = db.session.get(model_class, record_id)
        if not record:
            raise ValueError("Registro não encontrado")
        
        # Validar dados
        CRUDService._validate_data(table_config, data, is_update=True)
        
        # Obter campos editáveis
        editable_fields = PermissionService.get_editable_fields(current_user, table_config)
        editable_field_names = [f.name for f in editable_fields]
        
        # Atualizar apenas campos editáveis
        for field in editable_fields:
            if field.name in data:
                value = data[field.name]
                value = CRUDService._convert_value(field, value)
                setattr(record, field.name, value)
        
        try:
            db.session.commit()
            
            # Retornar registro atualizado
            return CRUDService.get_record(table_config_id, record_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao atualizar registro: {str(e)}")
    
    @staticmethod
    def delete_record(table_config_id, record_id):
        """
        Remove um registro.
        
        Args:
            table_config_id: ID da configuração da tabela
            record_id: ID do registro
        """
        # Verificar permissão de exclusão
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.DELETE
        ):
            raise PermissionError("Sem permissão para excluir registros desta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        model_class = TableService.get_table_model(table_config)
        
        if not model_class:
            raise ValueError("Tabela não existe no banco")
        
        record = db.session.get(model_class, record_id)
        if not record:
            raise ValueError("Registro não encontrado")
        
        try:
            db.session.delete(record)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao excluir registro: {str(e)}")
    
    @staticmethod
    def _validate_data(table_config, data, is_update=False):
        """Valida dados baseado na configuração dos campos."""
        for field in table_config.fields:
            value = data.get(field.name)
            
            # Verificar obrigatoriedade
            if field.is_required and not is_update and (value is None or value == ''):
                raise ValueError(f"Campo '{field.label}' é obrigatório")
            
            # Validar tamanho
            if value and field.size and len(str(value)) > field.size:
                raise ValueError(f"Campo '{field.label}' excede o tamanho máximo de {field.size} caracteres")
            
            # Validar tipo
            if value:
                try:
                    if field.field_type == 'number':
                        float(value)
                    elif field.field_type == 'integer':
                        int(value)
                    elif field.field_type == 'boolean':
                        if str(value).lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                            raise ValueError(f"Campo '{field.label}' deve ser booleano")
                except (ValueError, TypeError):
                    raise ValueError(f"Campo '{field.label}' tem tipo inválido")
    
    @staticmethod
    def _convert_value(field_config, value):
        """Converte valor para o tipo correto do campo."""
        if value is None:
            return None
        
        if field_config.field_type == 'number':
            return float(value)
        elif field_config.field_type == 'integer':
            return int(value)
        elif field_config.field_type == 'boolean':
            return str(value).lower() in ['true', '1', 'yes']
        elif field_config.field_type == 'date':
            # Assumir que já vem no formato correto
            return value
        else:
            return str(value)
