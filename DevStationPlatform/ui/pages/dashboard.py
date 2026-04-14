"""
Dashboard principal - DevStationPlatform
Métricas, KPIs e visão geral do sistema
"""

from nicegui import ui
from ui.components.layout import create_page_layout, metric_card, data_card
from ui.app import get_current_user
from core.kpi.collector import kpi_collector
from core.audit_logger import audit_logger
from datetime import datetime, timedelta


@create_page_layout("Dashboard")
def render():
    """Renderizar dashboard"""

    user_data = get_current_user()
    if not user_data:
        return

    # Header do dashboard
    with ui.row().classes('items-center justify-between w-full mb-6'):
        with ui.column().classes('gap-1'):
            ui.label('Dashboard').classes('text-white text-2xl font-bold')
            ui.label(f'Bem-vindo, {user_data.get("full_name", user_data.get("username"))}!').classes('text-[#8b949e]')

        with ui.row().classes('items-center gap-4'):
            ui.button('Atualizar', icon='refresh').classes('ds-btn-secondary')
            ui.button('Exportar', icon='download').classes('ds-btn-primary')

    # Métricas principais
    with ui.row().classes('gap-4 mb-6'):
        metric_card('Usuários Ativos', '42', 'people', 'blue')
        metric_card('Transações Hoje', '1,248', 'swap_horiz', 'green')
        metric_card('Tempo Médio', '2.4s', 'timer', 'orange')
        metric_card('Erros', '3', 'error', 'red')
        metric_card('Plugins', '8', 'extension', 'purple')

    # Grid de conteúdo
    with ui.row().classes('gap-6 w-full'):
        # Coluna esquerda
        with ui.column().classes('flex-1 gap-6'):
            # Gráfico de atividades
            with data_card('Atividades Recentes'):
                # Simular dados do gráfico
                activities = [
                    {'time': '09:00', 'user': 'admin', 'action': 'Login', 'status': 'success'},
                    {'time': '09:15', 'user': 'developer', 'action': 'DS_QUERY', 'status': 'success'},
                    {'time': '09:30', 'user': 'admin', 'action': 'User Created', 'status': 'success'},
                    {'time': '10:00', 'user': 'analyst', 'action': 'Report Export', 'status': 'warning'},
                    {'time': '10:30', 'user': 'developer', 'action': 'Plugin Install', 'status': 'success'},
                    {'time': '11:00', 'user': 'admin', 'action': 'System Backup', 'status': 'success'},
                ]

                with ui.table(columns=[
                    {'name': 'time', 'label': 'Hora', 'field': 'time'},
                    {'name': 'user', 'label': 'Usuário', 'field': 'user'},
                    {'name': 'action', 'label': 'Ação', 'field': 'action'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ], rows=activities).classes('w-full ds-table'):
                    pass

            # KPIs do sistema
            with data_card('KPIs do Sistema'):
                with ui.row().classes('gap-4 flex-wrap'):
                    kpis = [
                        {'name': 'Disponibilidade', 'value': '99.8%', 'target': '99.5%', 'trend': 'up'},
                        {'name': 'Performance', 'value': '96.2%', 'target': '95.0%', 'trend': 'up'},
                        {'name': 'Segurança', 'value': '100%', 'target': '100%', 'trend': 'stable'},
                        {'name': 'Satisfação', 'value': '4.8/5', 'target': '4.5/5', 'trend': 'up'},
                    ]

                    for kpi in kpis:
                        with ui.card().classes('flex-1 min-w-[200px] border border-[#30363d] p-4'):
                            with ui.column().classes('gap-2'):
                                ui.label(kpi['name']).classes('text-[#8b949e] text-sm')
                                with ui.row().classes('items-baseline gap-2'):
                                    ui.label(kpi['value']).classes('text-white text-2xl font-bold')
                                    trend_icon = 'trending_up' if kpi['trend'] == 'up' else 'trending_down' if kpi['trend'] == 'down' else 'trending_flat'
                                    ui.icon(trend_icon).classes(
                                        'text-green-400' if kpi['trend'] == 'up' else
                                        'text-red-400' if kpi['trend'] == 'down' else
                                        'text-yellow-400'
                                    )
                                ui.label(f'Meta: {kpi["target"]}').classes('text-[#8b949e] text-xs')

        # Coluna direita
        with ui.column().classes('w-96 gap-6'):
            # Status do sistema
            with data_card('Status do Sistema'):
                status_items = [
                    {'service': 'Banco de Dados', 'status': 'online', 'latency': '12ms'},
                    {'service': 'Autenticação', 'status': 'online', 'latency': '5ms'},
                    {'service': 'Auditoria', 'status': 'online', 'latency': '8ms'},
                    {'service': 'Plugins', 'status': 'online', 'latency': '15ms'},
                    {'service': 'API REST', 'status': 'online', 'latency': '25ms'},
                ]

                for item in status_items:
                    with ui.row().classes('items-center justify-between py-2 border-b border-[#30363d] last:border-0'):
                        with ui.row().classes('items-center gap-3'):
                            ui.icon('circle').classes(
                                'text-green-400' if item['status'] == 'online' else
                                'text-red-400' if item['status'] == 'offline' else
                                'text-yellow-400'
                            )
                            ui.label(item['service']).classes('text-white text-sm')
                        ui.label(item['latency']).classes('text-[#8b949e] text-sm')

            # Ações rápidas
            with data_card('Ações Rápidas'):
                quick_actions = [
                    {'icon': 'add', 'label': 'Novo Usuário', 'route': '/admin/users'},
                    {'icon': 'search', 'label': 'Consultar Logs', 'route': '/admin/audit'},
                    {'icon': 'code', 'label': 'Console SQL', 'route': '/tools/query'},
                    {'icon': 'design_services', 'label': 'UI Designer', 'route': '/designer'},
                ]

                with ui.column().classes('gap-2'):
                    for action in quick_actions:
                        ui.button(
                            action['label'],
                            icon=action['icon'],
                            on_click=lambda r=action['route']: ui.navigate.to(r)
                        ).classes('w-full justify-start ds-btn-secondary')

            # Informações do usuário
            with data_card('Sua Conta'):
                with ui.column().classes('gap-3'):
                    with ui.row().classes('items-center gap-3'):
                        with ui.card().classes('w-12 h-12 bg-blue-400 rounded-full items-center justify-center'):
                            ui.label(user_data.get('username', '?')[0].upper()).classes('text-white text-lg font-bold')
                        with ui.column().classes('gap-0'):
                            ui.label(user_data.get('full_name', user_data.get('username'))).classes('text-white font-medium')
                            ui.label(user_data.get('email', '')).classes('text-[#8b949e] text-sm')

                    with ui.row().classes('gap-2 flex-wrap'):
                        for profile in user_data.get('profiles', [])[:3]:
                            ui.label(profile).classes('bg-blue-500/20 text-blue-300 text-xs px-2 py-1 rounded')

                    ui.separator().classes('bg-[#30363d]')

                    with ui.row().classes('justify-between'):
                        ui.label('Último login:').classes('text-[#8b949e] text-sm')
                        ui.label(datetime.now().strftime('%d/%m %H:%M')).classes('text-white text-sm')

    # Rodapé do dashboard
    with ui.row().classes('mt-6 pt-4 border-t border-[#30363d] text-[#8b949e] text-sm justify-between'):
        ui.label(f'DevStationPlatform v1.0 · {datetime.now().strftime("%d/%m/%Y %H:%M")}')
        ui.label(f'Usuário: {user_data.get("username")} · Perfis: {", ".join(user_data.get("profiles", []))}')