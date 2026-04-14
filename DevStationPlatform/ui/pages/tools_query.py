"""
Console SQL (DS_QUERY) - DevStationPlatform
Execução de queries SQL com visualização de resultados
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.base import db_manager
from datetime import datetime
import traceback


TEMPLATES = {
    'SELECT': 'SELECT * FROM users LIMIT 10;',
    'INSERT': "INSERT INTO users (username, email) VALUES ('novo_user', 'email@exemplo.com');",
    'UPDATE': "UPDATE users SET is_active = 1 WHERE username = 'usuario';",
    'DELETE': "DELETE FROM users WHERE id = 0; -- cuidado!",
    'JOIN':   'SELECT u.username, p.code FROM users u\nJOIN user_profile_association upa ON u.id = upa.user_id\nJOIN profiles p ON upa.profile_id = p.id;',
    'TABLES': "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
    'SCHEMA': "SELECT sql FROM sqlite_master WHERE name = 'users';",
}


@create_page_layout("DS_QUERY — Console SQL")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    state = {
        'history': [],
        'result_cols': [],
        'result_rows': [],
        'exec_time': None,
        'row_count': 0,
        'error': None,
    }

    # ── helpers ───────────────────────────────────────────────────────────────
    def execute_query():
        sql = query_editor.value.strip()
        if not sql:
            return
        t0 = datetime.now()
        session = db_manager.get_session()
        try:
            from sqlalchemy import text
            result = session.execute(text(sql))
            elapsed = round((datetime.now() - t0).total_seconds() * 1000, 1)

            if result.returns_rows:
                keys = list(result.keys())
                rows_raw = result.fetchall()
                state['result_cols'] = [
                    {'name': k, 'label': k.upper(), 'field': k, 'align': 'left', 'sortable': True}
                    for k in keys
                ]
                state['result_rows'] = [
                    {k: (str(v) if v is not None else '—') for k, v in zip(keys, r)}
                    for r in rows_raw
                ]
                state['row_count'] = len(rows_raw)
            else:
                session.commit()
                affected = result.rowcount if hasattr(result, 'rowcount') else 0
                state['result_cols'] = [{'name': 'msg', 'label': 'Resultado', 'field': 'msg', 'align': 'left'}]
                state['result_rows'] = [{'msg': f'✅ Operação executada. Linhas afetadas: {affected}'}]
                state['row_count'] = affected

            state['exec_time'] = elapsed
            state['error'] = None
            state['history'].insert(0, {'sql': sql, 'time': datetime.now().strftime('%H:%M:%S'), 'ms': elapsed})
            if len(state['history']) > 50:
                state['history'] = state['history'][:50]

        except Exception as e:
            session.rollback()
            state['error'] = str(e)
            state['result_cols'] = []
            state['result_rows'] = []
        finally:
            session.close()
        refresh_results()

    def clear_query():
        query_editor.set_value('')
        state['result_cols'] = []
        state['result_rows'] = []
        state['error'] = None
        state['exec_time'] = None
        refresh_results()

    def set_template(tpl_key):
        query_editor.set_value(TEMPLATES[tpl_key])

    def open_history():
        with ui.dialog() as dlg, ui.card().classes('w-[700px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Histórico de Queries').classes('text-white text-lg font-bold mb-4')
            if not state['history']:
                ui.label('Nenhuma query executada ainda.').classes('text-[#8b949e]')
            else:
                with ui.scroll_area().classes('h-96 w-full'):
                    for entry in state['history']:
                        with ui.card().classes('bg-[#0d1117] border border-[#30363d] p-3 mb-2 cursor-pointer') \
                                .on('click', lambda e, s=entry['sql']: (query_editor.set_value(s), dlg.close())):
                            with ui.row().classes('items-center justify-between mb-1'):
                                ui.label(entry['time']).classes('text-[#8b949e] text-xs')
                                ui.label(f"{entry['ms']}ms").classes('text-green-400 text-xs')
                            ui.label(entry['sql'][:200]).classes('text-white text-xs font-mono')
            with ui.row().classes('justify-end mt-4'):
                ui.button('Fechar', on_click=dlg.close).props('flat color=grey-5 no-caps')
        dlg.open()

    # ── layout ────────────────────────────────────────────────────────────────
    # Header
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Console SQL (DS_QUERY)').classes('text-white text-2xl font-bold')
            ui.label('Execute queries SQL e visualize resultados').classes('text-[#8b949e] text-sm')
        with ui.row().classes('gap-2'):
            ui.button('Executar', icon='play_arrow', on_click=execute_query).props('color=green-7 no-caps')
            ui.button('Limpar',   icon='clear_all',  on_click=clear_query).props('flat color=grey-5 no-caps')
            ui.button('Histórico',icon='history',    on_click=open_history).props('flat color=grey-5 no-caps')

    with ui.row().classes('gap-4 w-full items-start'):
        # ── Coluna esquerda: editor ──────────────────────────────────────────
        with ui.column().classes('flex-1 gap-4'):
            with data_card('Editor SQL'):
                query_editor = ui.codemirror(
                    value='SELECT * FROM users LIMIT 10;',
                    language='SQL',
                    theme='dracula',
                ).classes('w-full h-52 rounded font-mono text-sm')

                # Templates rápidos
                with ui.row().classes('gap-2 mt-3 flex-wrap'):
                    for tpl in TEMPLATES:
                        ui.button(tpl, on_click=lambda k=tpl: set_template(k)) \
                            .props('dense no-caps outline color=blue-4').classes('text-xs')

            # Atalhos de teclado info
            with ui.row().classes('gap-4 text-xs text-[#8b949e]'):
                ui.label('Ctrl+Enter = Executar')
                ui.label('• Resultado max 1000 linhas')

        # ── Coluna direita: tabelas disponíveis ──────────────────────────────
        with ui.column().classes('w-56 gap-4'):
            with data_card('Tabelas'):
                session = db_manager.get_session()
                try:
                    from sqlalchemy import text
                    tbls = session.execute(
                        text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    ).fetchall()
                finally:
                    session.close()

                with ui.scroll_area().classes('h-64'):
                    for (tname,) in tbls:
                        ui.button(
                            tname,
                            on_click=lambda n=tname: query_editor.set_value(f'SELECT * FROM {n} LIMIT 20;')
                        ).props('flat no-caps align=left').classes('w-full text-[#8b949e] hover:text-white text-xs font-mono')

    # ── Área de resultados ────────────────────────────────────────────────────
    results_container = ui.column().classes('w-full mt-4')

    def refresh_results():
        results_container.clear()
        with results_container:
            if state['error']:
                with data_card('Erro'):
                    ui.label(state['error']).classes('text-red-400 font-mono text-sm')
                return

            if not state['result_rows']:
                return

            with data_card(f"Resultados — {state['row_count']} linha(s)  ·  {state['exec_time']}ms"):
                if len(state['result_rows']) > 1000:
                    ui.label(f'⚠ Exibindo 1000 de {len(state["result_rows"])} linhas.') \
                        .classes('text-yellow-400 text-sm mb-2')
                ui.table(
                    columns=state['result_cols'],
                    rows=state['result_rows'][:1000],
                ).classes('w-full ds-table text-xs').props('dense')

    # Ctrl+Enter para executar
    ui.keyboard(on_key=lambda e: execute_query() if e.key.name == 'Enter' and e.modifiers.ctrl else None)
