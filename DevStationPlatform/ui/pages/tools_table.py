"""
Navegador de Tabelas (DS_TAB) - DevStationPlatform
Exploração e visualização de tabelas do banco de dados (SQLite)
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.base import db_manager
from sqlalchemy import text, inspect
from datetime import datetime


@create_page_layout("DS_TAB — Navegador de Tabelas")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    state = {'selected': None, 'offset': 0, 'limit': 50}

    # ── helpers ───────────────────────────────────────────────────────────────
    def get_tables():
        session = db_manager.get_session()
        try:
            rows = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            ).fetchall()
            return [r[0] for r in rows]
        finally:
            session.close()

    def get_row_count(tname):
        session = db_manager.get_session()
        try:
            row = session.execute(text(f'SELECT COUNT(*) FROM "{tname}"')).fetchone()
            return row[0] if row else 0
        except:
            return '?'
        finally:
            session.close()

    def get_columns(tname):
        """Retorna lista de dicts com info das colunas via PRAGMA"""
        session = db_manager.get_session()
        try:
            rows = session.execute(text(f'PRAGMA table_info("{tname}")')).fetchall()
            # cid, name, type, notnull, dflt_value, pk
            return [{'cid': r[0], 'name': r[1], 'type': r[2],
                     'notnull': bool(r[3]), 'default': r[4], 'pk': bool(r[5])}
                    for r in rows]
        finally:
            session.close()

    def get_indexes(tname):
        session = db_manager.get_session()
        try:
            rows = session.execute(text(f'PRAGMA index_list("{tname}")')).fetchall()
            return [{'name': r[1], 'unique': bool(r[2])} for r in rows]
        finally:
            session.close()

    def get_data(tname, offset=0, limit=50):
        session = db_manager.get_session()
        try:
            rows = session.execute(
                text(f'SELECT * FROM "{tname}" LIMIT {limit} OFFSET {offset}')
            ).fetchall()
            cols_info = get_columns(tname)
            keys = [c['name'] for c in cols_info]
            return keys, [[str(v) if v is not None else '∅' for v in r] for r in rows]
        finally:
            session.close()

    # ── UI ────────────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Navegador de Tabelas (DS_TAB)').classes('text-white text-2xl font-bold')
            ui.label('Explore estrutura e dados do banco SQLite').classes('text-[#8b949e] text-sm')
        ui.button('Atualizar', icon='refresh', on_click=lambda: refresh_all()) \
            .props('flat color=grey-5 no-caps')

    tables = get_tables()
    inp_search = ui.input(placeholder='Filtrar tabelas...') \
        .classes('w-full mb-3').props('outlined dense dark color=blue-4 clearable')

    with ui.row().classes('gap-4 w-full items-start'):
        # ── Lista de tabelas ─────────────────────────────────────────────────
        with ui.column().classes('w-60'):
            with data_card('Tabelas do Banco'):
                table_list_col = ui.column().classes('w-full')

                def render_table_list(filt=''):
                    table_list_col.clear()
                    with table_list_col:
                        visible = [t for t in tables if filt.lower() in t.lower()]
                        if not visible:
                            ui.label('Nenhuma tabela.').classes('text-[#8b949e] text-xs')
                        for t in visible:
                            is_sel = state['selected'] == t
                            btn = ui.button(t, on_click=lambda tbl=t: select_table(tbl)) \
                                .props(f'flat no-caps align=left {"color=blue-4" if is_sel else "color=grey-5"}') \
                                .classes('w-full font-mono text-sm')

                render_table_list()
                inp_search.on('input', lambda e: render_table_list(e.args if isinstance(e.args, str) else inp_search.value))

        # ── Detalhes da tabela ───────────────────────────────────────────────
        detail_col = ui.column().classes('flex-1 gap-4')

        def select_table(tname):
            state['selected'] = tname
            state['offset'] = 0
            render_table_list(inp_search.value)
            render_detail(tname)

        def render_detail(tname):
            detail_col.clear()
            with detail_col:
                cols_info = get_columns(tname)
                indexes   = get_indexes(tname)
                row_count = get_row_count(tname)

                # Cabeçalho
                with ui.row().classes('items-center gap-4 mb-2'):
                    ui.label(tname).classes('text-white text-xl font-bold font-mono')
                    ui.badge(f'{row_count} linhas').props('color=blue-5')
                    ui.badge(f'{len(cols_info)} colunas').props('color=grey-7')

                with ui.tabs().classes('w-full') as tabs:
                    tab_struct = ui.tab('Estrutura', icon='schema')
                    tab_data   = ui.tab('Dados',     icon='table_rows')
                    tab_idx    = ui.tab('Índices',   icon='search')

                with ui.tab_panels(tabs, value=tab_struct).classes('w-full'):

                    # ── Estrutura ──────────────────────────────────────────
                    with ui.tab_panel(tab_struct):
                        with data_card('Colunas'):
                            struct_cols = [
                                {'name': 'cid',     'label': '#',       'field': 'cid',     'align': 'center'},
                                {'name': 'name',    'label': 'Nome',    'field': 'name',    'align': 'left'},
                                {'name': 'type',    'label': 'Tipo',    'field': 'type',    'align': 'left'},
                                {'name': 'notnull', 'label': 'NOT NULL','field': 'notnull', 'align': 'center'},
                                {'name': 'default', 'label': 'Default', 'field': 'default', 'align': 'left'},
                                {'name': 'pk',      'label': 'PK',      'field': 'pk',      'align': 'center'},
                            ]
                            struct_rows = [
                                {
                                    'cid':     c['cid'],
                                    'name':    c['name'],
                                    'type':    c['type'] or '—',
                                    'notnull': '✔' if c['notnull'] else '',
                                    'default': str(c['default']) if c['default'] is not None else '—',
                                    'pk':      '🔑' if c['pk'] else '',
                                }
                                for c in cols_info
                            ]
                            ui.table(columns=struct_cols, rows=struct_rows) \
                                .classes('w-full ds-table text-xs').props('dense')

                    # ── Dados ──────────────────────────────────────────────
                    with ui.tab_panel(tab_data):
                        data_area = ui.column().classes('w-full gap-3')
                        render_data_tab(tname, data_area)

                    # ── Índices ────────────────────────────────────────────
                    with ui.tab_panel(tab_idx):
                        with data_card('Índices'):
                            if not indexes:
                                ui.label('Nenhum índice cadastrado.').classes('text-[#8b949e]')
                            else:
                                idx_cols = [
                                    {'name': 'name',   'label': 'Nome',   'field': 'name',   'align': 'left'},
                                    {'name': 'unique', 'label': 'Único',  'field': 'unique', 'align': 'center'},
                                ]
                                idx_rows = [{'name': i['name'], 'unique': '✔' if i['unique'] else ''} for i in indexes]
                                ui.table(columns=idx_cols, rows=idx_rows) \
                                    .classes('w-full ds-table text-xs').props('dense')

        def render_data_tab(tname, container):
            container.clear()
            offset = state['offset']
            limit  = state['limit']
            keys, rows_raw = get_data(tname, offset, limit)
            total  = get_row_count(tname)

            with container:
                # Paginação
                with ui.row().classes('items-center gap-3'):
                    ui.label(f'Linhas {offset+1}–{min(offset+limit, total)} de {total}') \
                        .classes('text-[#8b949e] text-sm')
                    ui.button(icon='chevron_left',
                              on_click=lambda: prev_page(tname, container)) \
                        .props('flat dense').classes('text-white').set_enabled(offset > 0)
                    ui.button(icon='chevron_right',
                              on_click=lambda: next_page(tname, container)) \
                        .props('flat dense').classes('text-white').set_enabled(offset + limit < total)
                    ui.select([20, 50, 100, 200], value=limit,
                              on_change=lambda e: change_limit(tname, container, e.value)) \
                        .classes('w-24').props('outlined dense dark color=blue-4')

                if not rows_raw:
                    with data_card('Dados'):
                        ui.label('Tabela vazia.').classes('text-[#8b949e]')
                    return

                with data_card(f'Dados — {tname}'):
                    cols = [{'name': k, 'label': k, 'field': k, 'align': 'left', 'sortable': True}
                            for k in keys]
                    table_rows = [{k: v for k, v in zip(keys, r)} for r in rows_raw]
                    ui.table(columns=cols, rows=table_rows) \
                        .classes('w-full ds-table text-xs').props('dense')

        def prev_page(tname, container):
            state['offset'] = max(0, state['offset'] - state['limit'])
            render_data_tab(tname, container)

        def next_page(tname, container):
            state['offset'] += state['limit']
            render_data_tab(tname, container)

        def change_limit(tname, container, val):
            state['limit']  = val
            state['offset'] = 0
            render_data_tab(tname, container)

    def refresh_all():
        if state['selected']:
            render_detail(state['selected'])

    # Seleciona primeira tabela por padrão
    if tables:
        select_table(tables[0])
    else:
        with detail_col:
            ui.label('Nenhuma tabela encontrada no banco.').classes('text-[#8b949e]')
