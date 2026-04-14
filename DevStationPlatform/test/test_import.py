import sys
sys.path.insert(0, '.')

try:
    from main import *
    print('✅ main.py importado com sucesso')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()