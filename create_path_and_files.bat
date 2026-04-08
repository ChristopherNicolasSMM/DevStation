@echo off
echo Criando estrutura de diretorios e arquivos da DevStationPlatform...
echo.

REM Criar diretorio principal
mkdir DevStationPlatform 2>nul
cd DevStationPlatform

REM Criar estrutura core
mkdir core 2>nul
mkdir core\security 2>nul
mkdir core\models 2>nul

REM Criar arquivos do core
type nul > core\__init__.py
type nul > core\config.py
type nul > core\plugin_manager.py
type nul > core\menu_manager.py
type nul > core\transaction.py

REM Criar arquivos security
type nul > core\security\__init__.py
type nul > core\security\models.py
type nul > core\security\rbac.py
type nul > core\security\dynamic_profiles.py
type nul > core\security\profile_manager.py

REM Criar arquivos models
type nul > core\models\__init__.py
type nul > core\models\base.py
type nul > core\models\user.py
type nul > core\models\audit.py

REM Criar arquivos na raiz
type nul > config.yaml
type nul > main.py
type nul > requirements.txt
type nul > README.md

echo.
echo Estrutura criada com sucesso!
echo.
echo Diretorios e arquivos criados:
echo.
tree /F

pause