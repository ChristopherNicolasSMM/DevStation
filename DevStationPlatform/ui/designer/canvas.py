"""
Canvas do UI Designer - Área de drag & drop
"""

from nicegui import ui
import json
from typing import Dict, List, Any, Optional


class DesignerCanvas:
    """Canvas para arrastar e soltar componentes"""

    def __init__(self):
        self.components: List[Dict[str, Any]] = []
        self.selected_component: Optional[Dict[str, Any]] = None
        self.canvas_element = None
        self.drop_zone = None

    def render(self) -> ui.element:
        """Renderizar canvas"""
        with ui.card().classes('flex-1 border-2 border-dashed border-[#30363d] min-h-[500px]') as canvas:
            self.canvas_element = canvas

            # Área de drop
            with ui.column().classes('w-full h-full items-center justify-center') as drop_zone:
                self.drop_zone = drop_zone

                if not self.components:
                    # Mensagem inicial
                    ui.icon('dashboard').classes('text-6xl text-[#30363d] mb-4')
                    ui.label('Arraste componentes da paleta').classes('text-[#8b949e] text-lg')
                    ui.label('Solte aqui para adicionar ao canvas').classes('text-[#8b949e] text-sm')
                else:
                    # Renderizar componentes existentes
                    self._render_components()

        # Configurar eventos de drag & drop
        self._setup_drag_drop()

        return canvas

    def _render_components(self):
        """Renderizar componentes no canvas"""
        for i, component in enumerate(self.components):
            self._render_component(component, i)

    def _render_component(self, component: Dict[str, Any], index: int):
        """Renderizar um componente individual"""
        comp_type = component.get('type', 'unknown')
        props = component.get('properties', {})

        # Determinar classe de estilo baseada no tipo
        style_classes = 'p-4 border border-[#30363d] rounded-lg bg-[#161b22] hover:border-blue-400 cursor-move'

        # Renderizar baseado no tipo
        if comp_type == 'button':
            with ui.button(props.get('text', 'Button'), icon=props.get('icon')) \
                    .classes(f'{style_classes} w-auto') \
                    .on('click', lambda idx=index: self._select_component(idx)) as btn:
                component['element'] = btn

        elif comp_type == 'input':
            with ui.input(props.get('label', 'Input'), value=props.get('value', '')) \
                    .classes(f'{style_classes} w-64') \
                    .on('click', lambda idx=index: self._select_component(idx)) as inp:
                component['element'] = inp

        elif comp_type == 'label':
            with ui.label(props.get('text', 'Label')) \
                    .classes(f'{style_classes} w-auto') \
                    .on('click', lambda idx=index: self._select_component(idx)) as lbl:
                component['element'] = lbl

        elif comp_type == 'checkbox':
            with ui.checkbox(props.get('label', 'Checkbox'), value=props.get('checked', False)) \
                    .classes(f'{style_classes} w-auto') \
                    .on('click', lambda idx=index: self._select_component(idx)) as chk:
                component['element'] = chk

        elif comp_type == 'select':
            options = props.get('options', ['Option 1', 'Option 2'])
            with ui.select(options, value=props.get('value', ''), label=props.get('label', 'Select')) \
                    .classes(f'{style_classes} w-64') \
                    .on('click', lambda idx=index: self._select_component(idx)) as sel:
                component['element'] = sel

        elif comp_type == 'table':
            # Tabela simples
            columns = props.get('columns', [{'name': 'col1', 'label': 'Column 1'}])
            rows = props.get('rows', [{'col1': 'Data 1'}])
            with ui.table(columns=columns, rows=rows) \
                    .classes(f'{style_classes} w-full') \
                    .on('click', lambda idx=index: self._select_component(idx)) as tbl:
                component['element'] = tbl

        elif comp_type == 'card':
            with ui.card() \
                    .classes(f'{style_classes} w-64') \
                    .on('click', lambda idx=index: self._select_component(idx)) as card:
                with ui.column().classes('gap-2'):
                    if props.get('title'):
                        ui.label(props.get('title')).classes('text-white font-medium')
                    if props.get('content'):
                        ui.label(props.get('content')).classes('text-[#8b949e] text-sm')
                component['element'] = card

        elif comp_type == 'row':
            with ui.row() \
                    .classes(f'{style_classes} w-full gap-4') \
                    .on('click', lambda idx=index: self._select_component(idx)) as row:
                # Adicionar componentes filhos se existirem
                children = component.get('children', [])
                for child in children:
                    self._render_component(child, index)  # Nota: índice não é preciso para filhos
                component['element'] = row

        elif comp_type == 'column':
            with ui.column() \
                    .classes(f'{style_classes} w-full gap-4') \
                    .on('click', lambda idx=index: self._select_component(idx)) as col:
                # Adicionar componentes filhos se existirem
                children = component.get('children', [])
                for child in children:
                    self._render_component(child, index)  # Nota: índice não é preciso para filhos
                component['element'] = col

        # Adicionar indicador de seleção
        if self.selected_component == component:
            component['element'].classes('border-2 border-blue-400')

    def _setup_drag_drop(self):
        """Configurar eventos de drag & drop"""
        # Esta é uma implementação simplificada
        # Em uma implementação real, usaríamos JavaScript para drag & drop
        pass

    def add_component(self, component_type: str, properties: Dict[str, Any] = None):
        """Adicionar componente ao canvas"""
        if properties is None:
            properties = {}

        component = {
            'id': f'comp_{len(self.components)}_{component_type}',
            'type': component_type,
            'properties': properties,
            'position': {'x': 0, 'y': 0},  # Posição simplificada
            'children': []
        }

        self.components.append(component)
        self._refresh_canvas()

    def remove_component(self, component_id: str):
        """Remover componente do canvas"""
        self.components = [c for c in self.components if c['id'] != component_id]
        if self.selected_component and self.selected_component['id'] == component_id:
            self.selected_component = None
        self._refresh_canvas()

    def update_component(self, component_id: str, properties: Dict[str, Any]):
        """Atualizar propriedades de um componente"""
        for component in self.components:
            if component['id'] == component_id:
                component['properties'].update(properties)
                break
        self._refresh_canvas()

    def _select_component(self, index: int):
        """Selecionar um componente"""
        if 0 <= index < len(self.components):
            self.selected_component = self.components[index]
            self._refresh_canvas()

    def clear_canvas(self):
        """Limpar todos os componentes do canvas"""
        self.components.clear()
        self.selected_component = None
        self._refresh_canvas()

    def get_components(self) -> List[Dict[str, Any]]:
        """Obter lista de componentes"""
        return self.components.copy()

    def to_json(self) -> str:
        """Exportar canvas como JSON"""
        # Remover referências a elementos UI antes de serializar
        export_data = []
        for component in self.components:
            comp_copy = component.copy()
            comp_copy.pop('element', None)  # Remover referência ao elemento UI
            export_data.append(comp_copy)

        return json.dumps(export_data, indent=2)

    def from_json(self, json_str: str):
        """Importar canvas de JSON"""
        data = json.loads(json_str)
        self.components = data
        self.selected_component = None
        self._refresh_canvas()

    def _refresh_canvas(self):
        """Atualizar visualização do canvas"""
        # Em uma implementação real, reconstruiríamos o canvas
        # Para simplificar, apenas notificamos que precisa atualizar
        if self.drop_zone:
            # Limpar e reconstruir
            self.drop_zone.clear()
            if not self.components:
                ui.icon('dashboard').classes('text-6xl text-[#30363d] mb-4')
                ui.label('Arraste componentes da paleta').classes('text-[#8b949e] text-lg')
                ui.label('Solte aqui para adicionar ao canvas').classes('text-[#8b949e] text-sm')
            else:
                self._render_components()