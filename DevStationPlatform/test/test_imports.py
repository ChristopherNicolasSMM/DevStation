#!/usr/bin/env python3
"""
Script para testar importações do DevStationPlatform
"""

import sys
import traceback

sys.path.insert(0, '.')

print("=== Testando importações do DevStationPlatform ===\n")

# Testar importações core
print("1. Testando importações core...")
try:
    from core.config import Config
    print("   ✅ core.config.Config")
except Exception as e:
    print(f"   ❌ core.config.Config: {e}")
    traceback.print_exc()

try:
    from core.security.rbac import rbac
    print("   ✅ core.security.rbac.rbac")
except Exception as e:
    print(f"   ❌ core.security.rbac.rbac: {e}")
    traceback.print_exc()

try:
    from core.audit_logger import audit_logger
    print("   ✅ core.audit_logger.audit_logger")
except Exception as e:
    print(f"   ❌ core.audit_logger.audit_logger: {e}")
    traceback.print_exc()

try:
    from core.kpi.collector import kpi_collector
    print("   ✅ core.kpi.collector.kpi_collector")
except Exception as e:
    print(f"   ❌ core.kpi.collector.kpi_collector: {e}")
    traceback.print_exc()

print("\n2. Testando importações ui...")
try:
    import ui.app
    print("   ✅ ui.app")
except Exception as e:
    print(f"   ❌ ui.app: {e}")
    traceback.print_exc()

print("\n3. Testando importações de páginas...")
try:
    from ui.pages import login
    print("   ✅ ui.pages.login")
except Exception as e:
    print(f"   ❌ ui.pages.login: {e}")
    traceback.print_exc()

print("\n=== Teste completo ===")