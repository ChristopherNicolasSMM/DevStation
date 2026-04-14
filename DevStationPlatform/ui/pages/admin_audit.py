"""
DS_AUDIT — Auditoria e Changelog
Logs de auditoria com filtros avançados e detalhes completos
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.audit import AuditLog, ChangeLog
from core.models.base import db_manager
from datetime import datetime, timedelta
import json


@create_page_layout("DS_AUDIT — Auditoria")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    # ── DB helpers ────────────────────────────────────────────────────────
    def fetch_logs(term='', action='Todas', days=7, success_filter='Todos'):
        session = db_manager.get_session()
        try:
            since = datetime.utcnow() - timedelta(days=int(days))
            q = session.query(AuditLog).filter(AuditLog.timestamp >= since)
            if term:
                q = q.filter(AuditLog.user_name.ilike(f'%{term}%') |
                             AuditLog.object_name.ilike(f'%{term}%') |
                             AuditLog.transaction_code.ilike(f'%{term}%'))
            if action != 'Todas':
                q = q.filter(AuditLog.action_type == action)
            if success_filter == 'Sucesso':
                q = q.filter(AuditLog.success == True)
            elif success_filter == 'Erros':
                q = q.filter(AuditLog.success == False)
            logs = q.order_by(AuditLog.timestamp.desc()).limit(500).all()
            return [
                {
                    'id':         l.id,
                    'timestamp':  l.timestamp.strftime('%d/%m/%Y %H:%M:%S') if l.timestamp else '—',
                    'user_name':  l.user_name or '—',
                    'user_profiles': l.user_profile_codes or '—',
                    'transaction_code': l.transaction_code or '—',
                    'action_type': l.action_type or '—',
                    'object_type': l.object_type or '—',
                    'object_name': l.object_name or '—',
                    'success':    l.success,
                    'exec_ms':    l.execution_time_ms or 0,
                    'error_msg':  l.error_message or '',
                    'old_value':  json.dumps(l.old_value, ensure_ascii=False, indent=2) if l.old_value else '',
                    'new_value':  json.dumps(l.new_value, ensure_ascii=False, indent=2) if l.new_value else '',
                    'diff':       l.diff_summary or '',
                    'kpi_tags':   ', '.join(l.kpi_tags) if l.kpi_tags else '',
                }
                for l in logs
            ]
        finally:
            session.close()

    def fetch_changelog(days=30):
        session = db_manager.get_session()
        try:
            since = datetime.utcnow() - timedelta(days=int(days))
            chgs = (session.query(ChangeLog)
                    .filter(ChangeLog.timestamp >= since)
                    .order_by(ChangeLog.timestamp.desc())
                    .limit(200).all())
            return [
                {
                    'change_id':    c.change_id or '—',
                    'timestamp':    c.timestamp.strftime('%d/%m/%Y %H:%M') if c.timestamp else '—',
                    'author_name':  c.author_name or '—',
                    'object_type':  c.object_type or '—',
                    'object_code':  c.object_code or '—',
                    'change_type':  c.change_type or '—',
                    'change_summary': c.change_summary or '—',
                    'version_after':  c.version_after or '—',
                    'ticket_id':    c.ticket_id or '—',
                    'kpi_impact':   c.kpi_impact or '—',
                }
                for c in chgs
            ]
        finally:
            session.close()

    def open_detail(log_dict):
        with ui.dialog() as dlg, ui.card().classes('w-[680px] max-h-[80vh] bg-[#161b22] border border-[#30363d] p-6'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ok_icon  = 'check_circle' if log_dict['success'] else 'error'
                ok_color = 'text-green-400' if log_dict['success'] else 'text-red-400'
                ui.icon(ok_icon).classes(f'{ok_color} text-2xl')
                ui.label(f'Detalhe — {log_dict["transaction_code"]} · {log_dict["action_type"]}') \
                    .classes('text-white text-lg font-bold')

            with ui.scroll_area().classes('w-full max-h-[50vh]'):
                # Metadados principais
                with ui.row().classes('gap-4 flex-wrap mb-4'):
                    for label, val in [
                        ('Data/Hora',   log_dict['timestamp']),
                        ('Usuário',     log_dict['user_name']),
                        ('Perfis',      log_dict['user_profiles']),
                        ('Transação',   log_dict['transaction_code']),
                        ('Ação',        log_dict['action_type']),
                        ('Tipo Objeto', log_dict['object_type']),
                        ('Objeto',      log_dict['object_name']),
                        ('Tempo (ms)',  str(log_dict['exec_ms'])),
                        ('Tags KPI',    log_dict['kpi_tags'] or '—'),
                    ]:
                        with ui.column().classes('gap-0'):
                            ui.label(label).classes('text-[#8b949e] text-xs uppercase')
                            ui.label(str(val)).classes('text-white text-sm font-mono')

                if log_dict['error_msg']:
                    with ui.card().classes('bg-red-500/10 border border-red-500/20 p-3 w-full mt-3'):
                        ui.label('Mensagem de Erro').classes('text-red-400 text-xs font-semibold mb-1')
                        ui.label(log_dict['error_msg']).classes('text-white text-sm font-mono')

                if log_dict['diff']:
                    with ui.card().classes('bg-[#0d1117] border border-[#30363d] p-3 w-full mt-3'):
                        ui.label('Resumo da Alteração').classes('text-[#8b949e] text-xs mb-1')
                        ui.label(log_dict['diff']).classes('text-white text-sm')

                if log_dict['old_value'] or log_dict['new_value']:
                    with ui.row().classes('gap-4 mt-3'):
                        if log_dict['old_value']:
                            with ui.column().classes('flex-1'):
                                ui.label('ANTES').classes('text-red-400 text-xs font-semibold mb-1')
                                ui.codemirror(value=log_dict['old_value'], language='JSON', theme='dracula') \
                                    .classes('w-full h-32 text-xs rounded')
                        if log_dict['new_value']:
                            with ui.column().classes('flex-1'):
                                ui.label('DEPOIS').classes('text-green-400 text-xs font-semibold mb-1')
                                ui.codemirror(value=log_dict['new_value'], language='JSON', theme='dracula') \
                                    .classes('w-full h-32 text-xs rounded')

            with ui.row().classes('justify-end mt-4 border-t border-[#30363d] pt-4'):
                ui.button('Fechar', on_click=dlg.close).props('flat color=grey-5 no-caps')
        dlg.open()

    # ── Layout ────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Auditoria (DS_AUDIT)').classes('text-white text-2xl font-bold')
            ui.label('Rastreabilidade completa de todas as ações do sistema').classes('text-[#8b949e] text-sm')

    # Abas Audit / Changelog
    with ui.tabs().classes('w-full mb-0') as tabs:
        tab_audit  = ui.tab('Logs de Auditoria', icon='receipt_long')
        tab_change = ui.tab('Changelog',          icon='history')

    with ui.tab_panels(tabs, value=tab_audit).classes('w-full'):

        # ── Aba Auditoria ─────────────────────────────────────────────────
        with ui.tab_panel(tab_audit):
            with ui.row().classes('gap-3 mb-4 flex-wrap items-end'):
                inp_term   = ui.input(placeholder='Buscar usuário, transação ou objeto...') \
                    .classes('flex-1 min-w-48').props('outlined dense dark color=blue-4 clearable')
                sel_action = ui.select(
                    ['Todas','LOGIN','LOGOUT','CREATE','READ','UPDATE','DELETE','EXECUTE','EXPORT'],
                    value='Todas', label='Ação'
                ).classes('w-40').props('outlined dense dark color=blue-4')
                sel_result = ui.select(['Todos','Sucesso','Erros'], value='Todos', label='Resultado') \
                    .classes('w-36').props('outlined dense dark color=blue-4')
                sel_days   = ui.select([1, 7, 15, 30, 90], value=7, label='Período (dias)') \
                    .classes('w-36').props('outlined dense dark color=blue-4')
                ui.button('Filtrar', icon='filter_list',
                          on_click=lambda: refresh_audit()).props('color=blue-6 no-caps')

            kpi_row_audit    = ui.row().classes('gap-4 mb-4')
            audit_container  = ui.column().classes('w-full')

            def refresh_audit():
                logs = fetch_logs(inp_term.value, sel_action.value, sel_days.value, sel_result.value)
                total   = len(logs)
                errors  = sum(1 for l in logs if not l['success'])
                logins  = sum(1 for l in logs if l['action_type'] == 'LOGIN')
                uniq_u  = len(set(l['user_name'] for l in logs))

                kpi_row_audit.clear()
                with kpi_row_audit:
                    for label, val, color in [
                        ('Total de Eventos', total,   'text-white'),
                        ('Erros',            errors,  'text-red-400'),
                        ('Logins',           logins,  'text-green-400'),
                        ('Usuários Únicos',  uniq_u,  'text-blue-400'),
                    ]:
                        with ui.card().classes('bg-[#161b22] border border-[#30363d] px-6 py-3'):
                            ui.label(label).classes('text-[#8b949e] text-xs uppercase')
                            ui.label(str(val)).classes(f'{color} text-2xl font-bold')

                audit_container.clear()
                with audit_container:
                    if not logs:
                        with data_card('Eventos'):
                            ui.label('Nenhum registro encontrado.') \
                                .classes('text-[#8b949e] py-8 text-center w-full')
                        return

                    with data_card(f'Eventos — {total} registros'):
                        cols = [
                            {'name': 'timestamp',        'label': 'Data/Hora',  'field': 'timestamp',        'align': 'left', 'sortable': True},
                            {'name': 'user_name',        'label': 'Usuário',    'field': 'user_name',        'align': 'left', 'sortable': True},
                            {'name': 'transaction_code', 'label': 'Transação',  'field': 'transaction_code', 'align': 'left'},
                            {'name': 'action_type',      'label': 'Ação',       'field': 'action_type',      'align': 'center'},
                            {'name': 'object_name',      'label': 'Objeto',     'field': 'object_name',      'align': 'left'},
                            {'name': 'success',          'label': 'Status',     'field': 'success',          'align': 'center'},
                            {'name': 'exec_ms',          'label': 'ms',         'field': 'exec_ms',          'align': 'right'},
                            {'name': 'detail',           'label': '',           'field': 'id',               'align': 'center'},
                        ]
                        tbl = ui.table(columns=cols, rows=logs, row_key='id') \
                            .classes('w-full ds-table text-xs').props('dense')

                        tbl.add_slot('body-cell-success', '''
                            <q-td :props="props" class="text-center">
                                <q-badge :color="props.value ? \'green\' : \'red\'"
                                         :label="props.value ? \'✓ OK\' : \'✗ Erro\'"/>
                            </q-td>
                        ''')
                        tbl.add_slot('body-cell-detail', '''
                            <q-td :props="props" class="text-center">
                                <q-btn flat dense icon="info" color="blue-4"
                                       @click="$parent.$emit(\'detail\', props.row)"/>
                            </q-td>
                        ''')
                        tbl.on('detail', lambda e: open_detail(e.args))

            refresh_audit()

        # ── Aba Changelog ──────────────────────────────────────────────────
        with ui.tab_panel(tab_change):
            with ui.row().classes('gap-3 mb-4 items-end'):
                sel_chg_days = ui.select([7, 15, 30, 90, 365], value=30, label='Período (dias)') \
                    .classes('w-36').props('outlined dense dark color=blue-4')
                ui.button('Atualizar', icon='refresh',
                          on_click=lambda: refresh_changelog()) \
                    .props('color=blue-6 no-caps')

            chg_container = ui.column().classes('w-full')

            def refresh_changelog():
                changes = fetch_changelog(sel_chg_days.value)
                chg_container.clear()
                with chg_container:
                    if not changes:
                        with data_card('Changelog'):
                            ui.label('Nenhuma modificação registrada.') \
                                .classes('text-[#8b949e] py-8 text-center w-full')
                        return

                    TYPE_COLORS = {
                        'CREATE': 'green', 'MODIFY': 'blue',
                        'DELETE': 'red',   'RENAME': 'orange', 'MOVE': 'purple'
                    }
                    IMPACT_COLORS = {'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'grey-5'}

                    with data_card(f'Changelog — {len(changes)} registros'):
                        cols = [
                            {'name': 'change_id',     'label': 'ID',         'field': 'change_id',     'align': 'left'},
                            {'name': 'timestamp',     'label': 'Data/Hora',  'field': 'timestamp',     'align': 'left', 'sortable': True},
                            {'name': 'author_name',   'label': 'Autor',      'field': 'author_name',   'align': 'left'},
                            {'name': 'object_type',   'label': 'Tipo',       'field': 'object_type',   'align': 'center'},
                            {'name': 'object_code',   'label': 'Objeto',     'field': 'object_code',   'align': 'left'},
                            {'name': 'change_type',   'label': 'Operação',   'field': 'change_type',   'align': 'center'},
                            {'name': 'change_summary','label': 'Resumo',     'field': 'change_summary','align': 'left'},
                            {'name': 'version_after', 'label': 'Versão',     'field': 'version_after', 'align': 'center'},
                            {'name': 'ticket_id',     'label': 'Ticket',     'field': 'ticket_id',     'align': 'left'},
                            {'name': 'kpi_impact',    'label': 'Impacto',    'field': 'kpi_impact',    'align': 'center'},
                        ]
                        tbl = ui.table(columns=cols, rows=changes, row_key='change_id') \
                            .classes('w-full ds-table text-xs').props('dense')

                        tbl.add_slot('body-cell-change_type', '''
                            <q-td :props="props" class="text-center">
                                <q-badge :color="{ CREATE:\'green\', MODIFY:\'blue\', DELETE:\'red\', RENAME:\'orange\', MOVE:\'purple\' }[props.value] || \'grey\'"
                                         :label="props.value"/>
                            </q-td>
                        ''')
                        tbl.add_slot('body-cell-kpi_impact', '''
                            <q-td :props="props" class="text-center">
                                <q-badge :color="{ POSITIVE:\'green\', NEGATIVE:\'red\', NEUTRAL:\'grey-5\' }[props.value] || \'grey-7\'"
                                         :label="props.value || \'—\'"/>
                            </q-td>
                        ''')

            refresh_changelog()
