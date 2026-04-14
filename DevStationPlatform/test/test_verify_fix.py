"""
Testar a correção do método verify_password
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Testando correção do verify_password ===")

try:
    from core.models.base import db_manager
    from core.models.user import User

    session = db_manager.get_session()

    # Buscar usuário admin
    admin_user = session.query(User).filter_by(username="admin").first()

    if not admin_user:
        print("[ERRO] Usuário admin não encontrado!")
        session.close()
        sys.exit(1)

    print(f"1. Usuário encontrado: {admin_user.username}")
    print(f"   Hash da senha: {admin_user.password_hash[:30]}...")

    # Testar senhas
    test_cases = [
        ("admin123", True, "Senha correta do admin"),
        ("wrong123", False, "Senha errada"),
        ("dev123", False, "Senha do developer (não deve funcionar para admin)"),
    ]

    print("\n2. Testando verificações...")
    for password, expected, description in test_cases:
        result = admin_user.verify_password(password)
        status = "[OK]" if result == expected else "[ERRO]"
        expected_text = "deveria passar" if expected else "deveria falhar"
        print(f"   {status} {description}: '{password}' -> {result} ({expected_text})")

    # Testar usuário developer também
    print("\n3. Testando usuário developer...")
    dev_user = session.query(User).filter_by(username="developer").first()
    if dev_user:
        print(f"   Usuário: {dev_user.username}")

        dev_test_cases = [
            ("dev123", True, "Senha correta do developer"),
            ("admin123", False, "Senha do admin (não deve funcionar para developer)"),
            ("wrong123", False, "Senha errada"),
        ]

        for password, expected, description in dev_test_cases:
            result = dev_user.verify_password(password)
            status = "[OK]" if result == expected else "[ERRO]"
            expected_text = "deveria passar" if expected else "deveria falhar"
            print(f"   {status} {description}: '{password}' -> {result} ({expected_text})")
    else:
        print("   [ERRO] Usuário developer não encontrado!")

    session.close()
    print("\n[OK] Teste completo!")

except Exception as e:
    print(f"\n[ERRO] Erro: {e}")
    import traceback
    traceback.print_exc()