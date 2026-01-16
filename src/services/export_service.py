"""
Serviço para exportação de dados.
"""

import pandas as pd
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from flask import make_response
from db.database import db
from model.table_config import TableConfig
from services.table_service import TableService
from services.crud_service import CRUDService
from services.permission_service import PermissionService, PermissionType
from flask_login import current_user


class ExportService:
    """Serviço para exportação de dados."""
    
    @staticmethod
    def export_to_excel(table_config_id: int, filters: dict = None, 
                       visible_fields: list = None, filename: str = None) -> BytesIO:
        """
        Exporta dados para Excel.
        
        Args:
            table_config_id: ID da configuração da tabela
            filters: Filtros a aplicar
            visible_fields: Campos visíveis (None = todos)
            filename: Nome do arquivo (opcional)
        
        Returns:
            BytesIO com o arquivo Excel
        """
        # Verificar permissão
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.READ
        ):
            raise PermissionError("Sem permissão para exportar esta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        
        # Obter todos os registros (sem paginação)
        records, total, _, _ = CRUDService.list_records(
            table_config_id, page=1, per_page=10000, filters=filters
        )
        
        if not records:
            raise ValueError("Nenhum registro para exportar")
        
        # Filtrar campos visíveis
        if visible_fields:
            records = [
                {k: v for k, v in record.items() if k in visible_fields or k == 'id'}
                for record in records
            ]
        
        # Criar DataFrame
        df = pd.DataFrame(records)
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=table_config.name, index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_csv(table_config_id: int, filters: dict = None,
                     visible_fields: list = None) -> str:
        """
        Exporta dados para CSV.
        
        Args:
            table_config_id: ID da configuração da tabela
            filters: Filtros a aplicar
            visible_fields: Campos visíveis (None = todos)
        
        Returns:
            String CSV
        """
        # Verificar permissão
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.READ
        ):
            raise PermissionError("Sem permissão para exportar esta tabela")
        
        # Obter todos os registros
        records, total, _, _ = CRUDService.list_records(
            table_config_id, page=1, per_page=10000, filters=filters
        )
        
        if not records:
            return ""
        
        # Filtrar campos visíveis
        if visible_fields:
            records = [
                {k: v for k, v in record.items() if k in visible_fields or k == 'id'}
                for record in records
            ]
        
        # Criar DataFrame e converter para CSV
        df = pd.DataFrame(records)
        return df.to_csv(index=False)
    
    @staticmethod
    def export_to_pdf(table_config_id: int, filters: dict = None,
                     visible_fields: list = None, title: str = None) -> BytesIO:
        """
        Exporta dados para PDF.
        
        Args:
            table_config_id: ID da configuração da tabela
            filters: Filtros a aplicar
            visible_fields: Campos visíveis (None = todos)
            title: Título do relatório
        
        Returns:
            BytesIO com o arquivo PDF
        """
        # Verificar permissão
        if not PermissionService.has_table_permission(
            current_user, table_config_id, PermissionType.READ
        ):
            raise PermissionError("Sem permissão para exportar esta tabela")
        
        table_config = TableConfig.query.get_or_404(table_config_id)
        
        # Obter registros
        records, total, _, _ = CRUDService.list_records(
            table_config_id, page=1, per_page=1000, filters=filters
        )
        
        if not records:
            raise ValueError("Nenhum registro para exportar")
        
        # Filtrar campos visíveis
        if visible_fields:
            records = [
                {k: v for k, v in record.items() if k in visible_fields or k == 'id'}
                for record in records
            ]
        
        # Criar PDF em memória
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Título
        title_text = title or f"Relatório - {table_config.name}"
        elements.append(Paragraph(title_text, styles['Title']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Preparar dados da tabela
        if records:
            # Cabeçalho
            headers = list(records[0].keys())
            data = [headers]
            
            # Dados
            for record in records:
                row = [str(record.get(h, '')) for h in headers]
                data.append(row)
            
            # Criar tabela
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
