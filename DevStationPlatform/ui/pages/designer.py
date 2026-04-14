"""
UI Designer (DS_DESIGNER) - DevStationPlatform
Construtor visual de interfaces RAD
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
import json


COMPONENT_PALETTE = [
    {'key': 'label',    'icon': 'title',         'label': 'Label',     'category': 'Texto'},
    {'key': 'input',    'icon': 'input',          'label': 'Input',     'category': 'Formulário'},
    {'key': 'select',   'icon': 'arrow_drop_down','label': 'Select',    'category': 'Formulário'},
    {'key': 'checkbox', 'icon': 'check_box',      'label': 'Checkbox',  'category': 'Formulário'},
    {'key': 'button',   'icon': 'smart_button',   'label': 'Button',    'category': 'Ação'},
    {'key': 'table',    'icon': 'table_chart',    'label': 'Tabela',    'category': 'Dados'},
    {'key': 'card',     'icon': 'dashboard',      'label': 'Card',      'category': 'Layout'},
    {'key': 'row',      'icon': 'view_column',    'label': 'Row',       'category': 'Layout'},
    {'key': 'column',   'icon': 'view_stream',    'label': 'Column',    'category': 'Layout'},
    {'key': 'separator','icon': 'horizontal_rule','label': 'Separator', 'category': 'Layout'},
]

PROP_DEFAULTS = {
    'label':    {'text': 'Novo Label',  'classes': 'text-white text-base'},
    'input':    {'label': 'Campo',      'placeholder': '', 'password': False},
    'select':   {'label': 'Selecione',  'options': 'Opção 1\nOpção 2\nOpção 3'},
    'checkbox': {'text': 'Opção',       'value': False},
    'button':   {'text': 'Botão',       'color': 'blue-6', 'icon': ''},
    'table':    {'title': 'Tabela'},
    'card':     {'classes': 'bg-[#161b22] border border-[#30363d] p-4'},
    'row':      {'classes': 'gap-4 items-center'},
    'column':   {'classes': 'gap-4'},
    'separator':{'color': '#30363d'},
}

CATEGORIES = ['Texto', 'Formulário', 'Ação', 'Dados', 'Layout']


@create_page_layout("DS_DESIGNER — UI Designer")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    state = {
        'canvas': [],   # lista de componentes adicionados
        'selected_idx': None,
        'next_id': 1,
    }

    # ── helpers de código ─────────────────────────────────────────────────────
    def component_to_code(comp):
        k = comp['key']
        p = comp['props']
        indent = '    '
        if k == 'label':
            return f"ui.label({repr(p.get('text',''))}).classes({repr(p.get('classes',''))})"
        if k == 'input':
            return f"ui.input(label={repr(p.get('label',''))}, placeholder={repr(p.get('placeholder',''))})"
        if k == 'select':
            opts = [o.strip() for o in p.get('options','').splitlines() if o.strip()]
            return f"ui.select({opts}, label={repr(p.get('label',''))})"
        if k == 'checkbox':
            return f"ui.checkbox({repr(p.get('text',''))}, value={p.get('value', False)})"
        if k == 'button':
            icon_part = f", icon={repr(p.get('icon',''))}" if p.get('icon') else ''
            btn_color = p.get('color', 'blue-6')
        return f"ui.button({repr(p.get('text',''))}{icon_part}).props('color={btn_color} no-caps')"
        if k == 'table':
            return "ui.table(columns=[], rows=[]).classes('w-full ds-table')"
        if k == 'card':
            return f"with ui.card().classes({repr(p.get('classes',''))}):\n{indent}pass"
        if k == 'row':
            return f"with ui.row().classes({repr(p.get('classes',''))}):\n{indent}pass"
        if k == 'column':
            return f"with ui.column().classes({repr(p.get('classes',''))}):\n{indent}pass"
        if k == 'separator':
            return "ui.separator()"
        return f"# {k}"

    def generate_code():
        lines = ['from nicegui import ui', '', '']
        lines.append('@ui.page(\'/minha_pagina\')')
        lines.append('def minha_pagina():')
        if not state['canvas']:
            lines.append('    pass')
        else:
            for comp in state['canvas']:
                code = component_to_code(comp)
                for line in code.splitlines():
                    lines.append('    ' + line)
        return '\n'.join(lines)

    def render_canvas_preview():
        canvas_preview.clear()
        with canvas_preview:
            if not state['canvas']:
                with ui.column().classes('items-center justify-center h-48 w-full'):
                    ui.icon('add_box').classes('text-4xl text-[#30363d]')
                    ui.label('Arraste componentes ou clique na paleta') \
                        .classes('text-[#8b949e] text-sm mt-2')
                return
            for idx, comp in enumerate(state['canvas']):
                is_sel = state['selected_idx'] == idx
                with ui.row().classes(
                    f'w-full items-center gap-2 p-2 rounded cursor-pointer '
                    f'{"bg-blue-500/10 border border-blue-500/30" if is_sel else "hover:bg-white/5"}'
                ).on('click', lambda _, i=idx: select_component(i)):
                    ui.icon(next((c['icon'] for c in COMPONENT_PALETTE if c['key'] == comp['key']), 'widgets')) \
                        .classes('text-[#8b949e] text-base')
                    ui.label(f'{comp["key"]} — {list(comp["props"].values())[0] if comp["props"] else ""}') \
                        .classes('text-white text-sm flex-1 truncate')
                    with ui.row().classes('gap-1'):
                        ui.button(icon='arrow_upward',
                                  on_click=lambda _, i=idx: move_up(i)) \
                            .props('flat dense').classes('text-[#8b949e]')
                        ui.button(icon='arrow_downward',
                                  on_click=lambda _, i=idx: move_down(i)) \
                            .props('flat dense').classes('text-[#8b949e]')
                        ui.button(icon='delete',
                                  on_click=lambda _, i=idx: remove_component(i)) \
                            .props('flat dense').classes('text-red-400')

    def render_props_panel():
        props_panel.clear()
        idx = state['selected_idx']
        if idx is None or idx >= len(state['canvas']):
            with props_panel:
                ui.label('Selecione um componente').classes('text-[#8b949e] text-sm')
            return
        comp = state['canvas'][idx]
        with props_panel:
            ui.label(f'Propriedades — {comp["key"]}').classes('text-white text-sm font-bold mb-3')
            prop_inputs = {}
            for prop_key, prop_val in comp['props'].items():
                if isinstance(prop_val, bool):
                    prop_inputs[prop_key] = ui.checkbox(prop_key, value=prop_val)
                else:
                    prop_inputs[prop_key] = ui.input(label=prop_key, value=str(prop_val)) \
                        .classes('w-full').props('outlined dense dark color=blue-4')

            def apply_props():
                for pk, inp in prop_inputs.items():
                    if isinstance(inp, ui.checkbox):
                        comp['props'][pk] = inp.value
                    else:
                        comp['props'][pk] = inp.value
                render_canvas_preview()
                update_code()

            ui.button('Aplicar', on_click=apply_props).props('color=blue-6 no-caps dense').classes('mt-2')

    def update_code():
        code_area.set_value(generate_code())

    def add_component(key):
        comp = {
            'id':    state['next_id'],
            'key':   key,
            'props': dict(PROP_DEFAULTS.get(key, {})),
        }
        state['next_id'] += 1
        state['canvas'].append(comp)
        state['selected_idx'] = len(state['canvas']) - 1
        render_canvas_preview()
        render_props_panel()
        update_code()

    def select_component(idx):
        state['selected_idx'] = idx
        render_canvas_preview()
        render_props_panel()

    def remove_component(idx):
        state['canvas'].pop(idx)
        if state['selected_idx'] == idx:
            state['selected_idx'] = None
        elif state['selected_idx'] is not None and state['selected_idx'] > idx:
            state['selected_idx'] -= 1
        render_canvas_preview()
        render_props_panel()
        update_code()

    def move_up(idx):
        if idx > 0:
            state['canvas'][idx], state['canvas'][idx-1] = state['canvas'][idx-1], state['canvas'][idx]
            state['selected_idx'] = idx - 1
            render_canvas_preview()
            update_code()

    def move_down(idx):
        if idx < len(state['canvas']) - 1:
            state['canvas'][idx], state['canvas'][idx+1] = state['canvas'][idx+1], state['canvas'][idx]
            state['selected_idx'] = idx + 1
            render_canvas_preview()
            update_code()

    def clear_canvas():
        state['canvas'].clear()
        state['selected_idx'] = None
        render_canvas_preview()
        render_props_panel()
        update_code()

    def copy_code():
        ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(code_area.value)})')
        ui.notify('Código copiado!', type='positive')

    # ── UI ────────────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('UI Designer (DS_DESIGNER)').classes('text-white text-2xl font-bold')
            ui.label('Construtor visual de interfaces RAD').classes('text-[#8b949e] text-sm')
        with ui.row().classes('gap-2'):
            ui.button('Limpar Canvas', icon='delete_sweep', on_click=clear_canvas) \
                .props('flat color=grey-5 no-caps')
            ui.button('Copiar Código', icon='content_copy', on_click=copy_code) \
                .props('color=blue-6 no-caps')

    with ui.row().classes('gap-4 w-full items-start'):

        # ── Paleta (esquerda) ─────────────────────────────────────────────────
        with ui.column().classes('w-52 gap-3'):
            with data_card('Componentes'):
                for cat in CATEGORIES:
                    items = [c for c in COMPONENT_PALETTE if c['category'] == cat]
                    if not items:
                        continue
                    ui.label(cat).classes('text-[#8b949e] text-xs uppercase font-semibold mt-1')
                    for comp in items:
                        ui.button(
                            comp['label'],
                            icon=comp['icon'],
                            on_click=lambda k=comp['key']: add_component(k)
                        ).props('flat no-caps align=left dense').classes(
                            'w-full text-[#c9d1d9] hover:text-white text-sm'
                        )

        # ── Canvas (centro) ───────────────────────────────────────────────────
        with ui.column().classes('flex-1 gap-3'):
            with data_card('Canvas'):
                canvas_preview = ui.column().classes('w-full min-h-48 gap-1')
                render_canvas_preview()

        # ── Painel direito ────────────────────────────────────────────────────
        with ui.column().classes('w-56 gap-3'):
            with data_card('Propriedades'):
                props_panel = ui.column().classes('w-full gap-2')
                render_props_panel()

    # ── Código gerado ─────────────────────────────────────────────────────────
    with data_card('Código Gerado (NiceGUI)'):
        with ui.row().classes('items-center justify-between mb-2'):
            ui.label('Python / NiceGUI').classes('text-[#8b949e] text-xs font-mono')
            ui.button('Copiar', icon='content_copy', on_click=copy_code) \
                .props('flat dense color=blue-4 no-caps')
        code_area = ui.codemirror(
            value=generate_code(),
            language='Python',
            theme='dracula',
        ).classes('w-full h-48 rounded font-mono text-xs')
