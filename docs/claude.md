Eu estive vendo que com flet esta ocorrendo muitos problemas então vamos mudar para nicegui, abaixo tem a base que estou vendo aliando ao deepseek. Vamos mapear e executar este projeto. 


## 📝 Prompt para Claude (ou qualquer IA)

Copie e cole o texto abaixo em uma nova conversa com o Claude/ChatGPT/Cursor:

---

```markdown
# PROJETO: DevStationPlatform - Migração de Flet para NiceGUI

## CONTEXTO

Estou desenvolvendo uma plataforma RAD chamada DevStationPlatform, inspirada no SAP ECC/ABAP. Atualmente tenho o backend funcionando (Core Engine, RBAC, Autenticação, Banco de Dados) mas a interface em Flet está dando muitos problemas (ícones, métodos deprecados, API inconsistente).

**DECISÃO:** Abandonar completamente o Flet e migrar toda a interface para **NiceGUI**.

## O QUE JÁ FUNCIONA (BACKEND)

Manter TODO o código existente nas pastas:
- `core/` (config, plugin_manager, menu_manager, transaction)
- `core/security/` (rbac, models, auth, profile_manager)
- `core/models/` (user, audit, base)
- `main.py` (apenas a lógica de inicialização do banco, sem a parte Flet)

**O que deve ser removido/ignorado:**
- Todo código relacionado a Flet (imports ft, ft.Page, ft.app, etc.)
- Arquivos antigos de UI (auth.py com Flet, main.py com Flet)
- A pasta `static/` se tiver algo do Flet

## O QUE PRECISA SER CONSTRUÍDO (NOVO)

### 1. Interface Principal com NiceGUI

Criar um sistema de rotas NiceGUI que substitua as telas:

**Rotas necessárias:**
- `/` - Tela de login
- `/dashboard` - Dashboard principal após login
- `/admin/users` - Gestão de usuários
- `/admin/profiles` - Gestão de perfis de acesso
- `/admin/audit` - Visualização de logs
- `/tools/query` - Console SQL (DS_QUERY)
- `/tools/table` - Navegador de tabelas (DS_TAB)
- `/designer` - UI Designer com drag & drop (DS_DESIGNER)

### 2. Sistema de Autenticação

- Login com username/senha
- Sessão persistente via cookies/session
- Logout
- Verificação de permissões por rota

### 3. Layout e Estilo Visual

**ANEXAR HTML COM ESTILO VISUAL** (coloque seu HTML/CSS aqui)

Use este HTML como referência para:
- Paleta de cores (azul da barra lateral, fundo claro)
- Estilo dos cards (sombra, borda arredondada)
- Estilo dos botões (primário, secundário)
- Estilo das tabelas (bordas, hover)
- Sidebar/Drawer (menu lateral)
- Header (topo com usuário)

### 4. Componentes NiceGUI a serem utilizados

- `ui.page` - Layout base
- `ui.header` / `ui.left_drawer` - Menu lateral
- `ui.table` - Para listagens (ALVGrid)
- `ui.input`, `ui.select`, `ui.button` - Formulários
- `ui.card` - Cards de informação
- `ui.dialog` - Modais
- `ui.tabs` - Abas
- `ui.row`, `ui.column` - Layout responsivo
- `ui.label`, `ui.markdown` - Textos
- `ui.icon` - Ícones (usar Material Icons)

### 5. UI Designer com Drag & Drop (Importante)

Criar um designer visual onde o usuário pode:
- Arrastar componentes da paleta para o canvas
- Configurar propriedades do componente
- Gerar código Python (Flet ou CustomTkinter)
- Visualizar preview

**Paleta inicial de componentes:**
- Button, Text Input, Text Label, Checkbox, Select, Data Table, Card

### 6. Estrutura de Arquivos Esperada

```
DevStationPlatform/
├── core/                      # JÁ EXISTE (manter)
│   ├── config.py
│   ├── plugin_manager.py
│   ├── menu_manager.py
│   ├── transaction.py
│   ├── security/
│   │   ├── rbac.py
│   │   ├── auth.py
│   │   └── profile_manager.py
│   └── models/
│       ├── user.py
│       ├── audit.py
│       └── base.py
│
├── ui/                        # NOVO - Interface NiceGUI
│   ├── __init__.py
│   ├── app.py                 # App principal (main)
│   ├── pages/
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── admin_users.py
│   │   ├── admin_profiles.py
│   │   └── admin_audit.py
│   ├── components/
│   │   ├── alv_grid.py        # Componente de tabela
│   │   ├── form_builder.py    # Componente de formulário
│   │   └── layout.py          # Layout base (sidebar, header)
│   └── designer/              # UI Designer
│       ├── __init__.py
│       ├── canvas.py
│       ├── palette.py
│       ├── code_generator.py
│       └── preview.py
│
├── main.py                    # NOVO - Ponto de entrada (sem Flet)
├── requirements.txt           # Atualizar (remover flet, adicionar nicegui)
└── config.yaml                # JÁ EXISTE (manter)
```

### 7. main.py (Novo)

```python
from nicegui import ui
from ui.app import create_app

if __name__ == "__main__":
    create_app()
    ui.run(
        title="DevStationPlatform",
        favicon="🎯",
        dark=False,
        port=8080,
        reload=True  # Hot reload para desenvolvimento
    )
```

### 8. requirements.txt (Atualizado)

```
# Core (manter)
sqlalchemy>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
bcrypt>=4.0.0
python-jose[cryptography]>=3.3.0
passlib>=1.7.4

# Nova UI
nicegui>=1.4.0

# Utils
click>=8.1.0
rich>=13.7.0
```

## INSTRUÇÕES ESPECÍFICAS

1. **NÃO** reescreva o backend existente (core/). Aproveite todo o código de:
   - Autenticação (rbac.authenticate)
   - Modelos (User, Profile, Permission)
   - Sessão (page.data ou session storage)

2. **IGNORE** completamente o código Flet antigo. Comece do zero a UI.

3. **USE** o HTML anexado como referência visual (cores, espaçamentos, estilo)

4. **IMPLEMENTE** as transações DS_ como rotas NiceGUI:
   - `/tools/query` → DS_QUERY
   - `/tools/table` → DS_TAB
   - `/designer` → DS_DESIGNER

5. **GARANTA** que as permissões do RBAC sejam verificadas antes de carregar cada rota

6. **ENTREGUE** o código completo, organizado, com comentários em português/inglês

## ANEXO: ESTILO VISUAL (HTML/CSS)

[COLE AQUI SEU HTML COMPLETO COM O ESTILO QUE VOCÊ QUER]

---

Este HTML contém o estilo visual desejado para:
- Cores (sidebar azul #1976D2, fundo #f5f5f5)
- Cards com sombra e borda arredondada
- Botões (primário azul, secundário cinza)
- Tabelas com hover e bordas
- Layout com menu lateral e conteúdo principal

## RESULTADO ESPERADO

Após implementar, o sistema deve:
1. Iniciar em `http://localhost:8080`
2. Mostrar tela de login
3. Após login, mostrar dashboard com menu lateral
4. Ter todas as telas de administração funcionando
5. Ter o UI Designer com drag & drop funcionando
6. Gerar código Python (Flet) a partir do designer
```

---

## 📌 Como usar este prompt

1. **Copie todo o texto acima**
2. **Cole em uma nova conversa** com Claude/ChatGPT/Cursor
3. **Anexe seu HTML** com o estilo visual que você quer (onde está `[COLE AQUI SEU HTML]`)
4. **Envie** e aguarde o código

---

## ⚠️ Observações importantes

| Item | Explicação |
|------|------------|
| **Backend mantido** | Todo `core/` continua igual, só muda a UI |
| **Flet removido** | Não use mais `import flet` em lugar nenhum |
| **NiceGUI puro** | Interface toda em NiceGUI |
| **HTML anexado** | Use seu HTML como referência de estilo |
| **Drag & Drop** | Implementar com NiceGUI (suporta nativamente) |
