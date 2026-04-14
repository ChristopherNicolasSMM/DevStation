"""
Teste simples do banco de dados
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Teste Simples do Banco de Dados ===")

try:
    # Testar conexão básica
    print("1. Testando import do SQLAlchemy...")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    print("2. Criando engine...")
    engine = create_engine('sqlite:///devstation.db')

    print("3. Testando conexão...")
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"   Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")

    print("\n[OK] Conexão com banco de dados OK!")

except Exception as e:
    print(f"\n[ERRO] Erro: {e}")
    import traceback
    traceback.print_exc()