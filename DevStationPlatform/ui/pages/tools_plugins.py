"""
DS_PLUGINS — Gerenciador de Plugins
Instalação, configuração e status de plugins NDS_*
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
import json
import os
from datetime import datetime

# Catálogo de plugins disponíveis (mock para desenvolvimento)
PLUGIN_CATALOG = [
    {
        'id': 'fraterlink', 'name': 'FraterLink', 'version': '1.2.0',
        'description': 'Gestão de membros e atividades de lojas maçônicas',
        'author': 'DevStation Team', 'category': 'CRM',
        'transactions': ['NDS_FRATER_MEMBRO', 'NDS_FRATER_REUNIAO'],
        'installed': False, 'enabled': False,
    },
    {
        'id': 'inventory', 'name': 'Inventory Manager', 'version': '2.0.1',
        'description': 'Controle de estoque com rastreamento por lote e validade',
        'author': 'DevStation Team', 'category': 'Logística',
        'transactions': ['NDS_INVENTORY_PRODUCT', 'NDS_INVENTORY_MOVEMENT'],
        'installed': False, 'enabled': False,
    },
    {
        'id': 'brewfather', 'name': 'BrewFather Integration', 'version': '0.9.5',
        'description': 'Integração com Brewfather para gestão de receitas cervejeiras',
        'author': 'Community', 'category': 'Integração',
        'transactions': ['NDS_BREW_RECIPE', 'NDS_BREW_BATCH'],
        'installed': False, 'enabled': False,
    },
    {
        'id': 'hr_module', 'name': 'RH Básico', 'version': '1.0.0',
        'description': 'Gestão de funcionários, departamentos e folha de ponto',
        'author': 'DevStation Team', 'category': 'RH',
        'transactions': ['NDS_HR_EMPLOYEE', 'NDS_HR_DEPARTMENT'],
        'installed': True, 'enabled': True,
    },
    {
        'id': 'finance', 'name': 'Financeiro Simples', 'version': '1.1.2',
        'description': 'Contas a pagar/receber, centro de custo e fluxo de caixa',
        'author': 'DevStation Team', 'category': 'Finanças',
        'transactions': ['NDS_FIN_ACCOUNT', 'NDS_FIN_TRANSFER'],
        'installed': True, 'enabled': False,
    },
]

CAT_COLORS = {
    'CRM': 'blue-6', 'Logística': 'orange-6', 'Integração': 'purple-6',
    'RH': 'teal-6',  'Finanças': 'green-7',   'Outros': 'grey-6',
}


@create_page_layout("DS_PLUGINS — Gerenciador de Plugins")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    state = {'plugins': [dict(p) for p in PLUGIN_CATALOG], 'filter': 'Todos'}

    def open_plugin_detail(plugin):
        with ui.dialog() as dlg, \
             ui.card().classes('w-[600px] bg-[#161b22] border border-[#30363d] p-6'):
            cat_color = CAT_COLORS.get(plugin['category'], 'grey-6')
            with ui.row().classes('items-center gap-3 mb-4'):
                with ui.card().classes(f'w-12 h-12 bg-{cat_color}/20 rounded-lg items-center justify-center border border-{cat_color}/30'):
                    ui.icon('extension').classes(f'text-{cat_color} text-2xl')
                with ui.column().classes('gap-0'):
                    ui.label(plugin['name']).classes('text-white text-lg font-bold')
                    ui.label(f'v{plugin["version"]} · {plugin["category"]}') \
                        .classes('text-[#8b949e] text-sm')

            with ui.tabs().classes('w-full') as tabs:
                t_info  = ui.tab('Informações', icon='info')
                t_trans = ui.tab('Transações',  icon='swap_horiz')
                t_conf  = ui.tab('Configuração',icon='settings')

            with ui.tab_panels(tabs, value=t_info).classes('w-full pt-3'):

                with ui.tab_panel(t_info):
                    with ui.column().classes('gap-4'):
                        with ui.card().classes('bg-[#0d1117] border border-[#30363d] p-4'):
                            ui.label(plugin['description']).classes('text-[#c9d1d9] text-sm')
                        for label, val in [
                            ('ID',         plugin['id']),
                            ('Versão',     plugin['version']),
                            ('Categoria',  plugin['category']),
                            ('Autor',      plugin['author']),
                            ('Status',     '✅ Instalado e Ativo' if plugin['enabled'] else
                                           ('⚠ Instalado (inativo)' if plugin['installed'] else
                                            '❌ Não instalado')),
                        ]:
                            with ui.row().classes(
                                'items-center justify-between py-2 border-b border-[#30363d] last:border-0'
                            ):
                                ui.label(label).classes('text-[#8b949e] text-sm w-32')
                                ui.label(str(val)).classes('text-white text-sm')

                with ui.tab_panel(t_trans):
                    ui.label('Transações NDS_* fornecidas por este plugin:') \
                        .classes('text-[#8b949e] text-sm mb-3')
                    for tx in plugin.get('transactions', []):
                        with ui.row().classes(
                            'items-center gap-3 p-3 bg-[#0d1117] border border-[#30363d] rounded-lg mb-2'
                        ):
                            ui.icon('swap_horiz').classes('text-blue-400')
                            ui.label(tx).classes('text-white font-mono text-sm')
                            ui.label('NDS — Custom Transaction').classes('text-[#8b949e] text-xs ml-auto')

                with ui.tab_panel(t_conf):
                    if not plugin['installed']:
                        with ui.column().classes('items-center gap-3 py-8'):
                            ui.icon('extension_off').classes('text-4xl text-[#30363d]')
                            ui.label('Plugin não instalado.') \
                                .classes('text-[#8b949e] text-sm')
                    else:
                        ui.label('Configurações do plugin (em desenvolvimento)') \
                            .classes('text-[#8b949e] text-sm mb-4')
                        ui.input('Endpoint de integração').classes('w-full') \
                            .props('outlined dense dark color=blue-4 placeholder=https://api.exemplo.com')
                        ui.input('Chave de API').classes('w-full') \
                            .props('outlined dense dark color=blue-4 placeholder=sk-...')
                        ui.button('Salvar Configurações').props('color=blue-6 no-caps')

            with ui.row().classes('gap-2 justify-between mt-4 border-t border-[#30363d] pt-4'):
                ui.button('Fechar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                if not plugin['installed']:
                    ui.button('Instalar', icon='download',
                              on_click=lambda p=plugin: install_plugin(p, dlg)) \
                        .props('color=green-7 no-caps')
                elif plugin['enabled']:
                    ui.button('Desativar', icon='pause',
                              on_click=lambda p=plugin: toggle_plugin(p, False, dlg)) \
                        .props('color=orange-7 no-caps')
                else:
                    ui.button('Ativar', icon='play_arrow',
                              on_click=lambda p=plugin: toggle_plugin(p, True, dlg)) \
                        .props('color=blue-6 no-caps')
        dlg.open()

    def install_plugin(plugin, dlg=None):
        plugin['installed'] = True
        plugin['enabled']   = True
        ui.notify(f'Plugin "{plugin["name"]}" instalado com sucesso!', type='positive')
        if dlg:
            dlg.close()
        refresh()

    def toggle_plugin(plugin, enable, dlg=None):
        plugin['enabled'] = enable
        label = 'ativado' if enable else 'desativado'
        ui.notify(f'Plugin "{plugin["name"]}" {label}!',
                  type='positive' if enable else 'warning')
        if dlg:
            dlg.close()
        refresh()

    def uninstall_plugin(plugin):
        with ui.dialog() as dlg, \
             ui.card().classes('w-[400px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Confirmar Desinstalação').classes('text-white text-lg font-bold mb-2')
            with ui.row().classes(
                'items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg mb-4'
            ):
                ui.icon('warning').classes('text-red-400 text-2xl')
                ui.label(f'Desinstalar "{plugin["name"]}"? '
                         'Dados e transações NDS_* serão removidos.') \
                    .classes('text-[#c9d1d9] text-sm')

            def do_uninstall():
                plugin['installed'] = False
                plugin['enabled']   = False
                ui.notify(f'Plugin "{plugin["name"]}" desinstalado.', type='warning')
                dlg.close(); refresh()

            with ui.row().classes('gap-2 justify-end'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Desinstalar', on_click=do_uninstall).props('color=red-6 no-caps')
        dlg.open()

    # ── Header ────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Gerenciador de Plugins (DS_PLUGINS)').classes('text-white text-2xl font-bold')
            ui.label('Instale e gerencie extensões NDS_* da plataforma') \
                .classes('text-[#8b949e] text-sm')

    # Filtros + busca
    with ui.row().classes('items-center gap-3 mb-4'):
        inp_search = ui.input(placeholder='Buscar plugins...') \
            .classes('flex-1').props('outlined dense dark color=blue-4 clearable')
        all_cats = ['Todos'] + sorted(set(p['category'] for p in PLUGIN_CATALOG))
        sel_cat  = ui.select(all_cats, value='Todos', label='Categoria') \
            .classes('w-40').props('outlined dense dark color=blue-4')
        sel_status = ui.select(['Todos','Instalados','Ativos','Disponíveis'],
                               value='Todos', label='Status') \
            .classes('w-40').props('outlined dense dark color=blue-4')
        ui.button('Filtrar', icon='filter_list', on_click=lambda: refresh()) \
            .props('color=blue-6 no-caps')

    # KPI cards + conteúdo
    kpi_row       = ui.row().classes('gap-4 mb-4')
    content_col   = ui.column().classes('w-full gap-6')

    def refresh():
        plugins = state['plugins']
        # Aplicar filtros
        term   = inp_search.value.lower()
        cat    = sel_cat.value
        status = sel_status.value
        filtered = []
        for p in plugins:
            if term and term not in p['name'].lower() and term not in p['description'].lower():
                continue
            if cat != 'Todos' and p['category'] != cat:
                continue
            if status == 'Instalados' and not p['installed']:
                continue
            if status == 'Ativos' and not p['enabled']:
                continue
            if status == 'Disponíveis' and p['installed']:
                continue
            filtered.append(p)

        # KPIs
        kpi_row.clear()
        with kpi_row:
            total      = len(plugins)
            installed  = sum(1 for p in plugins if p['installed'])
            active     = sum(1 for p in plugins if p['enabled'])
            available  = total - installed
            for label, val, color in [
                ('Total',       total,     'text-white'),
                ('Instalados',  installed, 'text-blue-400'),
                ('Ativos',      active,    'text-green-400'),
                ('Disponíveis', available, 'text-[#8b949e]'),
            ]:
                with ui.card().classes('bg-[#161b22] border border-[#30363d] px-6 py-3'):
                    ui.label(label).classes('text-[#8b949e] text-xs uppercase')
                    ui.label(str(val)).classes(f'{color} text-2xl font-bold')

        content_col.clear()
        with content_col:
            if not filtered:
                with data_card('Plugins'):
                    ui.label('Nenhum plugin encontrado.') \
                        .classes('text-[#8b949e] text-center py-8 w-full')
                return

            # Plugins instalados/ativos
            installed_list = [p for p in filtered if p['installed']]
            if installed_list:
                with data_card(f'Instalados ({len(installed_list)})'):
                    with ui.row().classes('gap-4 flex-wrap'):
                        for p in installed_list:
                            _render_plugin_card(p, open_plugin_detail,
                                                toggle_plugin, uninstall_plugin)

            # Plugins disponíveis
            avail_list = [p for p in filtered if not p['installed']]
            if avail_list:
                with data_card(f'Disponíveis para Instalação ({len(avail_list)})'):
                    with ui.row().classes('gap-4 flex-wrap'):
                        for p in avail_list:
                            _render_plugin_card(p, open_plugin_detail,
                                                install_plugin, None)

    refresh()


def _render_plugin_card(plugin, on_detail, on_primary, on_uninstall):
    cat_color = CAT_COLORS.get(plugin['category'], 'grey-6')
    status_dot = ('text-green-400' if plugin['enabled'] else
                  'text-orange-400' if plugin['installed'] else
                  'text-[#30363d]')

    with ui.card().classes('bg-[#161b22] border border-[#30363d] p-4 w-72'):
        # Header do card
        with ui.row().classes('items-start justify-between mb-3'):
            with ui.row().classes('items-center gap-3'):
                with ui.card().classes(
                    f'w-10 h-10 rounded-lg items-center justify-center border border-[#30363d]'
                ):
                    ui.icon('extension').classes(f'text-{cat_color} text-xl')
                with ui.column().classes('gap-0'):
                    ui.label(plugin['name']).classes('text-white text-sm font-bold')
                    ui.label(f'v{plugin["version"]}').classes('text-[#8b949e] text-xs')
            ui.icon('circle').classes(f'{status_dot} text-xs')

        # Descrição
        ui.label(plugin['description']) \
            .classes('text-[#8b949e] text-xs mb-3 line-clamp-2')

        # Badges
        with ui.row().classes('gap-1 mb-3'):
            ui.badge(plugin['category']).props(f'color={cat_color}')
            if plugin['enabled']:
                ui.badge('Ativo').props('color=green-7')
            elif plugin['installed']:
                ui.badge('Inativo').props('color=orange-7')

        # Transações
        if plugin.get('transactions'):
            ui.label(f'{len(plugin["transactions"])} transações NDS_*') \
                .classes('text-[#8b949e] text-xs mb-3')

        # Ações
        with ui.row().classes('gap-2'):
            ui.button('Detalhes', icon='info',
                      on_click=lambda p=plugin: on_detail(p)) \
                .props('flat dense no-caps color=grey-5').classes('text-xs flex-1')
            if not plugin['installed']:
                ui.button('Instalar', icon='download',
                          on_click=lambda p=plugin: on_primary(p)) \
                    .props('dense no-caps color=green-7').classes('text-xs flex-1')
            elif plugin['enabled']:
                ui.button('Desativar',
                          on_click=lambda p=plugin: on_primary(p, False)) \
                    .props('dense no-caps color=orange-7').classes('text-xs')
                if on_uninstall:
                    ui.button(icon='delete',
                              on_click=lambda p=plugin: on_uninstall(p)) \
                        .props('flat dense color=red-4')
            else:
                ui.button('Ativar',
                          on_click=lambda p=plugin: on_primary(p, True)) \
                    .props('dense no-caps color=blue-6').classes('text-xs')
                if on_uninstall:
                    ui.button(icon='delete',
                              on_click=lambda p=plugin: on_uninstall(p)) \
                        .props('flat dense color=red-4')
