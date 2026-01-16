"""
Serviço para processamento de arquivos Excel.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from werkzeug.utils import secure_filename
from flask import current_app
from db.database import db
from model.table_config import TableConfig
from model.excel_mapping import ExcelMapping
from model.import_log import ImportLog
from services.table_service import TableService
from services.crud_service import CRUDService
from utils.excel_parser import ExcelParser
from flask_login import current_user


class ExcelService:
    """Serviço para operações com Excel."""
    
    @staticmethod
    def save_uploaded_file(file, table_config_id: int) -> str:
        """
        Salva arquivo enviado e retorna o caminho.
        
        Args:
            file: Arquivo do request
            table_config_id: ID da configuração da tabela
        
        Returns:
            Caminho do arquivo salvo
        """
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        # Criar subpasta por tabela
        table_folder = upload_folder / f"table_{table_config_id}"
        table_folder.mkdir(parents=True, exist_ok=True)
        
        # Nome seguro do arquivo
        filename = secure_filename(file.filename)
        file_path = table_folder / filename
        
        # Salvar arquivo
        file.save(str(file_path))
        
        return str(file_path)
    
    @staticmethod
    def process_excel_file(table_config_id: int, file_path: str, excel_mapping_id: Optional[int] = None) -> ImportLog:
        """
        Processa arquivo Excel e detecta divergências.
        
        Args:
            table_config_id: ID da configuração da tabela
            file_path: Caminho do arquivo
            excel_mapping_id: ID do mapeamento (opcional)
        
        Returns:
            ImportLog com os dados processados
        """
        table_config = TableConfig.query.get_or_404(table_config_id)
        
        # Obter mapeamento
        if excel_mapping_id:
            excel_mapping = ExcelMapping.query.get(excel_mapping_id)
        else:
            excel_mapping = ExcelMapping.query.filter_by(table_config_id=table_config_id).first()
        
        if not excel_mapping:
            raise ValueError("Mapeamento Excel não configurado para esta tabela")
        
        # Criar log de importação
        file_path_obj = Path(file_path)
        import_log = ImportLog(
            table_config_id=table_config_id,
            user_id=current_user.id if current_user.is_authenticated else None,
            filename=file_path_obj.name,
            file_path=file_path,
            file_size=file_path_obj.stat().st_size if file_path_obj.exists() else None,
            status='processing'
        )
        db.session.add(import_log)
        db.session.commit()
        
        try:
            # Parsear arquivo
            df = ExcelParser.parse_file(
                file_path,
                has_header=excel_mapping.has_header,
                start_row=excel_mapping.start_row
            )
            
            # Mapear colunas
            df_mapped = ExcelParser.map_columns(df, excel_mapping.column_mapping)
            
            # Converter para lista de dicionários
            records = ExcelParser.convert_to_dict_list(df_mapped)
            
            import_log.total_rows = len(records)
            
            # Verificar se tabela existe no banco
            if not TableService.table_exists(table_config.table_name):
                import_log.status = 'failed'
                import_log.error_message = "Tabela não existe no banco de dados"
                db.session.commit()
                return import_log
            
            # Obter modelo dinâmico
            model_class = TableService.get_table_model(table_config)
            if not model_class:
                import_log.status = 'failed'
                import_log.error_message = "Não foi possível obter modelo da tabela"
                db.session.commit()
                return import_log
            
            # Detectar divergências
            divergences = ExcelService._detect_divergences(
                table_config, records, model_class
            )
            
            import_log.divergences = divergences
            import_log.processed_data = records
            
            # Calcular estatísticas
            new_count = sum(1 for d in divergences if d['action'] == 'new')
            update_count = sum(1 for d in divergences if d['action'] == 'update')
            unchanged_count = sum(1 for d in divergences if d['action'] == 'unchanged')
            error_count = sum(1 for d in divergences if d['action'] == 'error')
            
            import_log.new_records = new_count
            import_log.updated_records = update_count
            import_log.unchanged_records = unchanged_count
            import_log.error_records = error_count
            
            import_log.status = 'completed'
            db.session.commit()
            
            return import_log
            
        except Exception as e:
            import_log.status = 'failed'
            import_log.error_message = str(e)
            db.session.commit()
            return import_log
    
    @staticmethod
    def _detect_divergences(table_config: TableConfig, records: List[Dict], model_class) -> List[Dict]:
        """
        Detecta divergências entre dados do Excel e dados no banco.
        
        Args:
            table_config: Configuração da tabela
            records: Registros do Excel
            model_class: Classe do modelo dinâmico
        
        Returns:
            Lista de divergências detectadas
        """
        divergences = []
        
        if not table_config.unique_key:
            # Sem chave única, todos são novos
            for idx, record in enumerate(records):
                divergences.append({
                    'index': idx,
                    'action': 'new',
                    'record': record,
                    'existing': None,
                    'differences': {}
                })
            return divergences
        
        # Buscar registros existentes
        existing_records = {}
        query = db.session.query(model_class)
        
        for record in records:
            # Construir filtro baseado na chave única
            filters = {}
            for field_name in table_config.unique_key:
                if field_name in record:
                    filters[field_name] = record[field_name]
            
            if not filters:
                # Chave única incompleta
                divergences.append({
                    'index': records.index(record),
                    'action': 'error',
                    'record': record,
                    'existing': None,
                    'differences': {},
                    'error': 'Chave única incompleta'
                })
                continue
            
            # Buscar registro existente
            query_filter = db.session.query(model_class)
            for field_name, value in filters.items():
                field_attr = getattr(model_class, field_name, None)
                if field_attr:
                    query_filter = query_filter.filter(field_attr == value)
            
            existing = query_filter.first()
            
            if existing:
                # Comparar campos
                differences = {}
                for field in table_config.fields:
                    field_name = field.name
                    excel_value = record.get(field_name)
                    existing_value = getattr(existing, field_name, None)
                    
                    # Normalizar valores para comparação
                    excel_str = str(excel_value) if excel_value is not None else ''
                    existing_str = str(existing_value) if existing_value is not None else ''
                    
                    if excel_str != existing_str:
                        differences[field_name] = {
                            'old': existing_value,
                            'new': excel_value
                        }
                
                if differences:
                    # Tem divergências
                    divergences.append({
                        'index': records.index(record),
                        'action': 'update',
                        'record': record,
                        'existing': {f.name: getattr(existing, f.name) for f in table_config.fields},
                        'differences': differences,
                        'record_id': existing.id
                    })
                else:
                    # Sem alterações
                    divergences.append({
                        'index': records.index(record),
                        'action': 'unchanged',
                        'record': record,
                        'existing': {f.name: getattr(existing, f.name) for f in table_config.fields},
                        'differences': {},
                        'record_id': existing.id
                    })
            else:
                # Novo registro
                divergences.append({
                    'index': records.index(record),
                    'action': 'new',
                    'record': record,
                    'existing': None,
                    'differences': {}
                })
        
        return divergences
    
    @staticmethod
    def apply_approved_changes(import_log_id: int, approved_items: List[Dict]) -> Dict[str, int]:
        """
        Aplica alterações aprovadas do Excel.
        
        Args:
            import_log_id: ID do log de importação
            approved_items: Lista de itens aprovados [{"index": 0, "fields": ["campo1", "campo2"]}]
        
        Returns:
            Dicionário com estatísticas de aplicação
        """
        import_log = ImportLog.query.get_or_404(import_log_id)
        table_config = TableConfig.query.get_or_404(import_log.table_config_id)
        
        if import_log.status != 'completed':
            raise ValueError("Importação não está completa")
        
        if not import_log.divergences:
            raise ValueError("Nenhuma divergência encontrada")
        
        stats = {
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        # Criar conjunto de índices aprovados
        approved_indices = {item['index'] for item in approved_items}
        
        try:
            for divergence in import_log.divergences:
                idx = divergence['index']
                
                if idx not in approved_indices:
                    continue
                
                # Obter campos aprovados para este item
                item = next((i for i in approved_items if i['index'] == idx), None)
                approved_fields = item.get('fields', []) if item else []
                
                if divergence['action'] == 'new':
                    # Criar novo registro
                    try:
                        CRUDService.create_record(table_config.id, divergence['record'])
                        stats['created'] += 1
                    except Exception as e:
                        stats['errors'] += 1
                        print(f"Erro ao criar registro {idx}: {e}")
                
                elif divergence['action'] == 'update':
                    # Atualizar registro existente
                    record_id = divergence.get('record_id')
                    if not record_id:
                        stats['errors'] += 1
                        continue
                    
                    # Preparar dados apenas com campos aprovados
                    update_data = {}
                    for field_name in approved_fields:
                        if field_name in divergence['record']:
                            update_data[field_name] = divergence['record'][field_name]
                    
                    if update_data:
                        try:
                            CRUDService.update_record(table_config.id, record_id, update_data)
                            stats['updated'] += 1
                        except Exception as e:
                            stats['errors'] += 1
                            print(f"Erro ao atualizar registro {idx}: {e}")
            
            # Atualizar status do log
            import_log.status = 'approved'
            import_log.approved_by_id = current_user.id if current_user.is_authenticated else None
            from sqlalchemy.sql import func
            import_log.approved_at = func.now()
            db.session.commit()
            
            return stats
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao aplicar alterações: {str(e)}")
