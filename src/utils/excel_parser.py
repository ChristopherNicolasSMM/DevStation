"""
Parser de arquivos Excel e CSV.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import json


class ExcelParser:
    """Parser para arquivos Excel e CSV."""
    
    @staticmethod
    def parse_file(file_path: str, has_header: bool = True, start_row: int = 1) -> pd.DataFrame:
        """
        Parse um arquivo Excel ou CSV.
        
        Args:
            file_path: Caminho do arquivo
            has_header: Se a primeira linha é cabeçalho
            start_row: Linha inicial dos dados (1-indexed)
        
        Returns:
            DataFrame do pandas com os dados
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Determinar extensão
        ext = file_path_obj.suffix.lower()
        
        try:
            if ext in ['.xlsx', '.xls']:
                # Excel
                if has_header:
                    df = pd.read_excel(file_path, header=0, skiprows=start_row - 1)
                else:
                    df = pd.read_excel(file_path, header=None, skiprows=start_row - 1)
            elif ext == '.csv':
                # CSV
                if has_header:
                    df = pd.read_csv(file_path, header=0, skiprows=start_row - 1)
                else:
                    df = pd.read_csv(file_path, header=None, skiprows=start_row - 1)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {ext}")
            
            return df
        except Exception as e:
            raise Exception(f"Erro ao parsear arquivo: {str(e)}")
    
    @staticmethod
    def map_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Mapeia colunas do Excel para campos da tabela.
        
        Args:
            df: DataFrame do pandas
            column_mapping: Dicionário {coluna_excel: campo_tabela}
                           Pode ser índice (0, 1, 2...) ou nome da coluna
        
        Returns:
            DataFrame com colunas renomeadas
        """
        # Criar dicionário de mapeamento
        rename_dict = {}
        
        for excel_col, table_field in column_mapping.items():
            # Tentar como índice primeiro
            try:
                col_index = int(excel_col)
                if col_index < len(df.columns):
                    rename_dict[df.columns[col_index]] = table_field
            except ValueError:
                # Tentar como nome de coluna
                if excel_col in df.columns:
                    rename_dict[excel_col] = table_field
        
        # Renomear colunas
        df_renamed = df.rename(columns=rename_dict)
        
        return df_renamed
    
    @staticmethod
    def convert_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Converte DataFrame para lista de dicionários.
        
        Args:
            df: DataFrame do pandas
        
        Returns:
            Lista de dicionários
        """
        # Substituir NaN por None
        df = df.where(pd.notna(df), None)
        
        # Converter para lista de dicionários
        records = df.to_dict('records')
        
        return records
    
    @staticmethod
    def detect_duplicates(records: List[Dict], unique_key_fields: List[str]) -> Dict[int, Dict]:
        """
        Detecta registros duplicados baseado na chave única.
        
        Args:
            records: Lista de registros
            unique_key_fields: Lista de campos que compõem a chave única
        
        Returns:
            Dicionário {índice: dados_duplicado} para registros duplicados
        """
        seen = {}
        duplicates = {}
        
        for idx, record in enumerate(records):
            # Construir chave única
            key_parts = []
            for field in unique_key_fields:
                value = record.get(field)
                key_parts.append(str(value) if value is not None else '')
            
            unique_key = '|'.join(key_parts)
            
            if unique_key in seen:
                duplicates[idx] = seen[unique_key]
            else:
                seen[unique_key] = idx
        
        return duplicates
