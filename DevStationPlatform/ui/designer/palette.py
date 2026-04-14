"""
Paleta de Componentes do UI Designer
Componentes arrastáveis para o canvas
"""

from nicegui import ui
from typing import Dict, List, Any, Callable


class ComponentPalette:
    """Paleta de componentes arrastáveis"""

    def __init__(self, on_component_selected: Callable[[str, Dict[str, Any]], None]):
        self.on_component_selected = on_component_selected
        self.components = self._get_available_components()

    def render(self) -> ui.element:
        """Renderizar paleta de componentes"""
        with ui.card().classes('w-64 border border-[#30363d]'):
            ui.label('Componentes').classes('text-white text-lg font-semibold mb-4')

            with ui.column().classes('gap-2'):
                # Componentes básicos
                self._render_component_group('Básicos', [
                    ('button', 'Botão', 'smart_button'),
                    ('input', 'Campo de Texto', 'input'),
                    ('label', 'Rótulo', 'label'),
                    ('checkbox', 'Checkbox', 'check_box'),
                    ('select', 'Seleção', 'arrow_drop_down'),
                ])

                # Componentes de layout
                self._render_component_group('Layout', [
                    ('row', 'Linha', 'view_week'),
                    ('column', 'Coluna', 'view_column'),
                    ('card', 'Card', 'dashboard'),
                ])

                # Componentes de dados
                self._render_component_group('Dados', [
                    ('table', 'Tabela', 'table_chart'),
                ])

                # Separador
                ui.separator().classes('my-2 bg-[#30363d]')

                # Ações
                with ui.column().classes('gap-1'):
                    ui.button('Limpar Canvas', icon='clear_all', on_click=self._clear_canvas) \
                        .classes('w-full justify-start ds-btn-secondary text-sm')
                    ui.button('Exportar Design', icon='download', on_click=self._export_design) \
                        .classes('w-full justify-start ds-btn-secondary text-sm')
                    ui.button('Importar Design', icon='upload', on_click=self._import_design) \
                        .classes('w-full justify-start ds-btn-secondary text-sm')

        return ui.get_slot()

    def _render_component_group(self, group_name: str, components: List[tuple]):
        """Renderizar grupo de componentes"""
        with ui.expansion(group_name, icon='category').classes('w-full'):
            with ui.column().classes('gap-1 pl-2'):
                for comp_type, comp_name, comp_icon in components:
                    self._render_component_item(comp_type, comp_name, comp_icon)

    def _render_component_item(self, comp_type: str, comp_name: str, comp_icon: str):
        """Renderizar item de componente individual"""
        with ui.card().classes('border border-[#30363d] hover:border-blue-400 cursor-move p-2') \
                .on('click', lambda t=comp_type: self._select_component(t)):
            with ui.row().classes('items-center gap-3'):
                ui.icon(comp_icon).classes('text-blue-400')
                ui.label(comp_name).classes('text-white text-sm')
                ui.icon('drag_handle').classes('text-[#8b949e] ml-auto')

    def _select_component(self, component_type: str):
        """Selecionar componente da paleta"""
        default_props = self._get_default_properties(component_type)
        self.on_component_selected(component_type, default_props)

    def _get_default_properties(self, component_type: str) -> Dict[str, Any]:
        """Obter propriedades padrão para um tipo de componente"""
        defaults = {
            'button': {
                'text': 'Novo Botão',
                'icon': None,
                'color': 'primary',
                'size': 'md'
            },
            'input': {
                'label': 'Campo de Texto',
                'value': '',
                'placeholder': 'Digite algo...',
                'type': 'text'
            },
            'label': {
                'text': 'Novo Rótulo',
                'size': 'md',
                'color': 'white'
            },
            'checkbox': {
                'label': 'Nova Checkbox',
                'checked': False
            },
            'select': {
                'label': 'Nova Seleção',
                'options': ['Opção 1', 'Opção 2', 'Opção 3'],
                'value': ''
            },
            'table': {
                'columns': [
                    {'name': 'col1', 'label': 'Coluna 1'},
                    {'name': 'col2', 'label': 'Coluna 2'}
                ],
                'rows': [
                    {'col1': 'Dado 1', 'col2': 'Dado 2'},
                    {'col1': 'Dado 3', 'col2': 'Dado 4'}
                ]
            },
            'card': {
                'title': 'Novo Card',
                'content': 'Conteúdo do card aqui...',
                'elevation': 1
            },
            'row': {
                'gap': 4,
                'align': 'start',
                'justify': 'start'
            },
            'column': {
                'gap': 4,
                'align': 'start',
                'justify': 'start'
            }
        }

        return defaults.get(component_type, {})

    def _get_available_components(self) -> List[Dict[str, Any]]:
        """Obter lista de componentes disponíveis"""
        return [
            {
                'type': 'button',
                'name': 'Botão',
                'icon': 'smart_button',
                'description': 'Botão clicável com texto e ícone',
                'category': 'Básicos'
            },
            {
                'type': 'input',
                'name': 'Campo de Texto',
                'icon': 'input',
                'description': 'Campo para entrada de texto',
                'category': 'Básicos'
            },
            {
                'type': 'label',
                'name': 'Rótulo',
                'icon': 'label',
                'description': 'Texto estático para labels',
                'category': 'Básicos'
            },
            {
                'type': 'checkbox',
                'name': 'Checkbox',
                'icon': 'check_box',
                'description': 'Caixa de seleção',
                'category': 'Básicos'
            },
            {
                'type': 'select',
                'name': 'Seleção',
                'icon': 'arrow_drop_down',
                'description': 'Dropdown com opções',
                'category': 'Básicos'
            },
            {
                'type': 'row',
                'name': 'Linha',
                'icon': 'view_week',
                'description': 'Container horizontal',
                'category': 'Layout'
            },
            {
                'type': 'column',
                'name': 'Coluna',
                'icon': 'view_column',
                'description': 'Container vertical',
                'category': 'Layout'
            },
            {
                'type': 'card',
                'name': 'Card',
                'icon': 'dashboard',
                'description': 'Container com borda e sombra',
                'category': 'Layout'
            },
            {
                'type': 'table',
                'name': 'Tabela',
                'icon': 'table_chart',
                'description': 'Tabela de dados',
                'category': 'Dados'
            }
        ]

    def _clear_canvas(self):
        """Limpar canvas (será conectado ao canvas)"""
        ui.notify('Funcionalidade: Limpar Canvas', type='info')

    def _export_design(self):
        """Exportar design (será conectado ao canvas)"""
        ui.notify('Funcionalidade: Exportar Design', type='info')

    def _import_design(self):
        """Importar design (será conectado ao canvas)"""
        ui.notify('Funcionalidade: Importar Design', type='info')

    def get_component_info(self, component_type: str) -> Dict[str, Any]:
        """Obter informações sobre um tipo de componente"""
        for comp in self.components:
            if comp['type'] == component_type:
                return comp.copy()
        return {}