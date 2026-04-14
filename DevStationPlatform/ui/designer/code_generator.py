"""
Gerador de Código do UI Designer
Gera código Python (NiceGUI/Flet) a partir do design
"""

from typing import Dict, List, Any
import json


class CodeGenerator:
    """Gerador de código a partir de componentes do designer"""

    def __init__(self):
        self.indent_level = 0
        self.indent_size = 4

    def generate_nicegui_code(self, components: List[Dict[str, Any]]) -> str:
        """Gerar código NiceGUI a partir dos componentes"""
        if not components:
            return self._generate_empty_code()

        code_lines = [
            'from nicegui import ui',
            '',
            'def create_ui():',
            '    """Interface gerada pelo DevStation Designer"""',
            ''
        ]

        # Adicionar cada componente
        for component in components:
            comp_code = self._generate_component_code(component, 1)
            code_lines.extend(comp_code)

        # Adicionar função de execução
        code_lines.extend([
            '',
            'if __name__ == "__main__":',
            '    create_ui()',
            '    ui.run()'
        ])

        return '\n'.join(code_lines)

    def generate_flet_code(self, components: List[Dict[str, Any]]) -> str:
        """Gerar código Flet a partir dos componentes"""
        if not components:
            return self._generate_empty_flet_code()

        code_lines = [
            'import flet as ft',
            '',
            'def main(page: ft.Page):',
            '    """Interface gerada pelo DevStation Designer"""',
            '    page.title = "App Gerado"',
            '    page.theme_mode = ft.ThemeMode.DARK',
            ''
        ]

        # Adicionar cada componente
        for component in components:
            comp_code = self._generate_flet_component_code(component, 1)
            code_lines.extend(comp_code)

        # Adicionar função de execução
        code_lines.extend([
            '',
            'if __name__ == "__main__":',
            '    ft.app(target=main)'
        ])

        return '\n'.join(code_lines)

    def _generate_component_code(self, component: Dict[str, Any], indent: int) -> List[str]:
        """Gerar código para um componente NiceGUI"""
        comp_type = component.get('type', 'unknown')
        props = component.get('properties', {})
        children = component.get('children', [])

        indent_str = ' ' * (indent * self.indent_size)

        if comp_type == 'button':
            text = props.get('text', 'Button')
            icon = props.get('icon')
            if icon:
                return [f'{indent_str}ui.button("{text}", icon="{icon}")']
            else:
                return [f'{indent_str}ui.button("{text}")']

        elif comp_type == 'input':
            label = props.get('label', 'Input')
            value = props.get('value', '')
            placeholder = props.get('placeholder', '')
            if placeholder:
                return [f'{indent_str}ui.input("{label}", value="{value}", placeholder="{placeholder}")']
            else:
                return [f'{indent_str}ui.input("{label}", value="{value}")']

        elif comp_type == 'label':
            text = props.get('text', 'Label')
            return [f'{indent_str}ui.label("{text}")']

        elif comp_type == 'checkbox':
            label = props.get('label', 'Checkbox')
            checked = props.get('checked', False)
            return [f'{indent_str}ui.checkbox("{label}", value={checked})']

        elif comp_type == 'select':
            label = props.get('label', 'Select')
            options = props.get('options', ['Option 1', 'Option 2'])
            options_str = json.dumps(options)
            return [f'{indent_str}ui.select({options_str}, label="{label}")']

        elif comp_type == 'table':
            columns = props.get('columns', [{'name': 'col1', 'label': 'Column 1'}])
            rows = props.get('rows', [{'col1': 'Data 1'}])
            columns_str = json.dumps(columns)
            rows_str = json.dumps(rows)
            return [f'{indent_str}ui.table(columns={columns_str}, rows={rows_str})']

        elif comp_type == 'card':
            title = props.get('title', 'Card')
            content = props.get('content', 'Content')
            code_lines = [
                f'{indent_str}with ui.card():',
                f'{indent_str}    ui.label("{title}").classes("text-white font-medium")',
                f'{indent_str}    ui.label("{content}").classes("text-[#8b949e] text-sm")'
            ]
            return code_lines

        elif comp_type == 'row':
            code_lines = [f'{indent_str}with ui.row():']
            for child in children:
                child_code = self._generate_component_code(child, indent + 1)
                code_lines.extend(child_code)
            return code_lines

        elif comp_type == 'column':
            code_lines = [f'{indent_str}with ui.column():']
            for child in children:
                child_code = self._generate_component_code(child, indent + 1)
                code_lines.extend(child_code)
            return code_lines

        else:
            return [f'{indent_str}# Componente desconhecido: {comp_type}']

    def _generate_flet_component_code(self, component: Dict[str, Any], indent: int) -> List[str]:
        """Gerar código para um componente Flet"""
        comp_type = component.get('type', 'unknown')
        props = component.get('properties', {})
        children = component.get('children', [])

        indent_str = ' ' * (indent * self.indent_size)

        if comp_type == 'button':
            text = props.get('text', 'Button')
            return [f'{indent_str}page.add(ft.ElevatedButton("{text}"))']

        elif comp_type == 'input':
            label = props.get('label', 'Input')
            value = props.get('value', '')
            return [f'{indent_str}page.add(ft.TextField(label="{label}", value="{value}"))']

        elif comp_type == 'label':
            text = props.get('text', 'Label')
            return [f'{indent_str}page.add(ft.Text("{text}"))']

        elif comp_type == 'checkbox':
            label = props.get('label', 'Checkbox')
            checked = props.get('checked', False)
            return [f'{indent_str}page.add(ft.Checkbox(label="{label}", value={checked}))']

        elif comp_type == 'select':
            label = props.get('label', 'Select')
            options = props.get('options', ['Option 1', 'Option 2'])
            options_str = json.dumps([ft.dropdown.Option(o) for o in options])
            return [f'{indent_str}page.add(ft.Dropdown(label="{label}", options={options_str}))']

        elif comp_type == 'row':
            code_lines = [f'{indent_str}row = ft.Row([])']
            for child in children:
                child_code = self._generate_flet_component_code(child, indent + 1)
                # Extrair apenas a criação do componente
                for line in child_code:
                    if 'page.add(' in line:
                        comp_var = line.split('page.add(')[1].split(')')[0]
                        code_lines.append(f'{indent_str}row.controls.append({comp_var})')
            code_lines.append(f'{indent_str}page.add(row)')
            return code_lines

        elif comp_type == 'column':
            code_lines = [f'{indent_str}col = ft.Column([])']
            for child in children:
                child_code = self._generate_flet_component_code(child, indent + 1)
                # Extrair apenas a criação do componente
                for line in child_code:
                    if 'page.add(' in line:
                        comp_var = line.split('page.add(')[1].split(')')[0]
                        code_lines.append(f'{indent_str}col.controls.append({comp_var})')
            code_lines.append(f'{indent_str}page.add(col)')
            return code_lines

        else:
            return [f'{indent_str}# Componente Flet: {comp_type}']

    def _generate_empty_code(self) -> str:
        """Gerar código para canvas vazio"""
        return '''from nicegui import ui

def create_ui():
    """Interface gerada pelo DevStation Designer"""
    ui.label("Interface vazia - Adicione componentes no designer!")

if __name__ == "__main__":
    create_ui()
    ui.run()
'''

    def _generate_empty_flet_code(self) -> str:
        """Gerar código Flet para canvas vazio"""
        return '''import flet as ft

def main(page: ft.Page):
    """Interface gerada pelo DevStation Designer"""
    page.title = "App Gerado"
    page.theme_mode = ft.ThemeMode.DARK
    page.add(ft.Text("Interface vazia - Adicione componentes no designer!"))

if __name__ == "__main__":
    ft.app(target=main)
'''

    def generate_preview_html(self, components: List[Dict[str, Any]]) -> str:
        """Gerar preview HTML dos componentes"""
        if not components:
            return '<div class="empty-canvas">Canvas vazio</div>'

        html_parts = ['<div class="designer-preview">']

        for component in components:
            html_parts.append(self._generate_component_html(component))

        html_parts.append('</div>')
        return '\n'.join(html_parts)

    def _generate_component_html(self, component: Dict[str, Any]) -> str:
        """Gerar HTML para um componente"""
        comp_type = component.get('type', 'unknown')
        props = component.get('properties', {})

        if comp_type == 'button':
            text = props.get('text', 'Button')
            return f'<button class="preview-button">{text}</button>'

        elif comp_type == 'input':
            label = props.get('label', 'Input')
            value = props.get('value', '')
            return f'<div class="preview-input"><label>{label}</label><input type="text" value="{value}"></div>'

        elif comp_type == 'label':
            text = props.get('text', 'Label')
            return f'<div class="preview-label">{text}</div>'

        elif comp_type == 'checkbox':
            label = props.get('label', 'Checkbox')
            checked = 'checked' if props.get('checked', False) else ''
            return f'<div class="preview-checkbox"><input type="checkbox" {checked}><label>{label}</label></div>'

        elif comp_type == 'select':
            label = props.get('label', 'Select')
            options = props.get('options', ['Option 1', 'Option 2'])
            options_html = ''.join([f'<option>{opt}</option>' for opt in options])
            return f'<div class="preview-select"><label>{label}</label><select>{options_html}</select></div>'

        elif comp_type == 'table':
            columns = props.get('columns', [{'name': 'col1', 'label': 'Column 1'}])
            rows = props.get('rows', [{'col1': 'Data 1'}])

            headers = ''.join([f'<th>{col["label"]}</th>' for col in columns])
            rows_html = ''
            for row in rows:
                cells = ''.join([f'<td>{row.get(col["name"], "")}</td>' for col in columns])
                rows_html += f'<tr>{cells}</tr>'

            return f'''
            <div class="preview-table">
                <table>
                    <thead><tr>{headers}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            '''

        elif comp_type == 'card':
            title = props.get('title', 'Card')
            content = props.get('content', 'Content')
            return f'''
            <div class="preview-card">
                <h3>{title}</h3>
                <p>{content}</p>
            </div>
            '''

        else:
            return f'<div class="preview-unknown">Componente: {comp_type}</div>'