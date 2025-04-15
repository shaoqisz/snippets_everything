import sys
import re
import os
import json
import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection


def format(color, style=''):
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format([200, 120, 50], 'bold'),
    'operator': format([150, 150, 150]),
    'brace': format('darkGray'),
    'defclass': format([220, 220, 250], 'bold'),
    'string': format([20, 110, 100]),
    'comment': format([70, 70, 70], 'italic'),
    'self': format([150, 85, 140], 'italic'),
    'numbers': format([100, 150, 190]),
    'placeholder': format([255, 0, 0], 'bold')
}


class PythonHighlighter(QSyntaxHighlighter):
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        rules += [
            (r'\bself\b', 0, STYLES['self']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'#[^\n]*', 0, STYLES['comment']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            (r'\$\w+', 0, STYLES['placeholder'])
        ]

        rules += [
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),
        ]

        self.rules = [(re.compile(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)

class CppHighlighter(QSyntaxHighlighter):
    keywords = [
        'alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel',
        'atomic_commit', 'atomic_noexcept', 'auto', 'bitand', 'bitor',
        'bool', 'break', 'case', 'catch', 'char', 'char8_t', 'char16_t',
        'char32_t', 'class', 'compl', 'concept', 'const', 'consteval',
        'constexpr', 'constinit', 'const_cast', 'continue', 'co_await',
        'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do',
        'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export',
        'extern', 'false', 'float', 'for', 'friend', 'goto', 'if',
        'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept',
        'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private',
        'protected', 'public', 'reflexpr', 'register', 'reinterpret_cast',
        'requires', 'return', 'short', 'signed', 'sizeof', 'static',
        'static_assert', 'static_cast', 'struct', 'switch', 'synchronized',
        'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef',
        'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void',
        'volatile', 'wchar_t', 'while', 'xor', 'xor_eq',
    ]

    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CppHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CppHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CppHighlighter.braces]

        rules += [
            (r'//[^\n]*', 0, STYLES['comment']),
            (r'/\*.*?\*/', 0, STYLES['comment']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        self.rules = [(re.compile(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)


class PlainTextHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        self.rules = [(re.compile(r'\$\w+'), 0, STYLES['placeholder'])]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.search(text)
            while index:
                length = index.end(nth) - index.start(nth)
                self.setFormat(index.start(nth), length, format)
                index = expression.search(text, index.end(nth))
        self.setCurrentBlockState(0)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.input_widgets = {}
        # 使用 QSplitter 分割界面
        splitter = QSplitter(Qt.Horizontal)

        # 左侧 TreeView
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Title', 'Type', 'Created Time'])
        self.tree_view.setModel(self.model)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)  # 不允许修改内容
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)  # 设置选择模式为单选
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.tree_view.clicked.connect(self.on_tree_item_clicked)
        splitter.addWidget(self.tree_view)

        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 显示 title 和 type 的控件
        info_layout = QHBoxLayout()
        self.title_lineedit = QLineEdit()
        # 允许 title_lineedit 被修改
        self.title_lineedit.setReadOnly(False)
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(['Plain text', 'Python', 'C++'])

        # 新增删除和新增按钮
        self.delete_button = QPushButton("-")
        self.add_button = QPushButton("+")
        
        self.delete_button.clicked.connect(self.delete_snippet)
        self.add_button.clicked.connect(self.add_snippet)

        info_layout.addWidget(self.title_lineedit)
        info_layout.addWidget(self.type_combobox)
        info_layout.addWidget(self.add_button)
        info_layout.addWidget(self.delete_button)

        right_layout.addLayout(info_layout)

        self.text_edit = QTextEdit()
        self.text_edit_replaced = QTextEdit()
        self.text_edit_replaced.setReadOnly(True)

        self.python_highlighter = PythonHighlighter(self.text_edit.document())
        self.cpp_highlighter = CppHighlighter(self.text_edit.document())
        self.plain_text_highlighter = PlainTextHighlighter(self.text_edit.document())

        self.python_highlighter_replaced = PythonHighlighter(self.text_edit_replaced.document())
        self.cpp_highlighter_replaced = CppHighlighter(self.text_edit_replaced.document())
        self.plain_text_highlighter_replaced = PlainTextHighlighter(self.text_edit_replaced.document())

        self.text_edit.textChanged.connect(self.update_input_layout)
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.text_edit_replaced)

        self.input_layout = QVBoxLayout()
        right_layout.addLayout(self.input_layout)

        # # 保留 replace 按钮
        # self.replace_button = QPushButton("Replace")
        # self.replace_button.clicked.connect(self.replace_placeholders)
        # right_layout.addWidget(self.replace_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_snippet)
        right_layout.addWidget(self.save_button)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.load_snippets()
        self.current_snippet_file = None

        index = self.model.index(0, 0)
        self.select_tree_item(index)
        self.on_tree_item_clicked(index)

    def load_snippets(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Title', 'Type', 'Created Time'])
        snippets = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        snippets.append(snippet)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        # 按创建时间排序
        snippets.sort(key=lambda x: x.get('created_time', ''))
        for snippet in snippets:
            title = snippet.get('title', 'Unknown')
            snippet_type = snippet.get('type', 'Unknown')
            created_time = snippet.get('created_time', '')
            title_item = QStandardItem(title)
            type_item = QStandardItem(snippet_type)
            created_time_item = QStandardItem(created_time)
            self.model.appendRow([title_item, type_item, created_time_item])

    def on_tree_item_clicked(self, index):
        title = self.model.itemFromIndex(self.model.index(index.row(), 0)).text()
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        
                        
                        if snippet.get('title') == title:
                            
                            # self.text_edit.blockSignals(True)
                            
                            self.title_lineedit.setText(title)
                            type_index = self.type_combobox.findText(snippet.get('type', 'Plain text'))
                            self.type_combobox.setCurrentIndex(type_index)
                            
                            self.text_edit.setPlainText(snippet.get('content', ''))
                            self.update_input_layout()
                            self.current_snippet_file = file_path
                            # 加载占位符的值
                            
                            self.apply_highlighter(snippet.get('type', ''))

                            for placeholder, value in snippet.items():
                                if placeholder.startswith('$') and placeholder in self.input_widgets:
                                    print(f'placeholder={placeholder} value={value}')
                                    self.input_widgets[placeholder].setText(value)

                            # self.text_edit.blockSignals(False)

                            self.replace_placeholders()
                            
                            break
                
                
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def update_input_layout(self):
        print('update_input_layout')
        # 保存之前输入框的值
        previous_values = {placeholder: input_field.text() for placeholder, input_field in self.input_widgets.items()}

        # 清空现有的输入框及布局
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.deleteLater()

        self.input_widgets = {}
        code = self.text_edit.toPlainText()
        placeholders = re.findall(r'\$\w+', code)

        unique_placeholders = []
        for placeholder in placeholders:
            if placeholder not in unique_placeholders:
                unique_placeholders.append(placeholder)

        for placeholder in unique_placeholders:
            label = QLineEdit(placeholder)
            label.setReadOnly(True)
            input_field = QLineEdit()
            # 恢复之前输入框的值
            if placeholder in previous_values:
                input_field.setText(previous_values[placeholder])
                input_field.textChanged.connect(self.replace_placeholders)

            print(f'placeholder={placeholder} input_field={input_field}')
            self.input_widgets[placeholder] = input_field

            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(input_field)
            self.input_layout.addLayout(hbox)

    def replace_placeholders(self):
        code = self.text_edit.toPlainText()
        for placeholder, input_field in self.input_widgets.items():
            replacement = input_field.text()
            if replacement:
                code = code.replace(placeholder, replacement)
        self.text_edit_replaced.setPlainText(code)

    def save_snippet(self):
        if not self.current_snippet_file:
            print("No snippet is currently selected.")
            return
        title = self.title_lineedit.text()
        snippet_type = self.type_combobox.currentText()
        content = self.text_edit.toPlainText()
        placeholders = re.findall(r'\$\w+', content)

        # 获取当前时间作为创建时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建包含占位符值的字典
        placeholder_dict = {placeholder: self.input_widgets[placeholder].text() if placeholder in self.input_widgets else '' for placeholder in placeholders}

        snippet = {
            'type': snippet_type,
            'title': title,
            'content': content,
            'created_time': now,
            **placeholder_dict
        }

        try:
            with open(self.current_snippet_file, 'w', encoding='utf-8') as f:
                json.dump(snippet, f, ensure_ascii=False, indent=4)
            self.load_snippets()
        except Exception as e:
            print(f"Error saving snippet: {e}")

    def apply_highlighter(self, snippet_type):
        if snippet_type == 'Python':
            self.python_highlighter.setDocument(self.text_edit.document())
            self.python_highlighter_replaced.setDocument(self.text_edit_replaced.document())

        elif snippet_type == 'C++':
            self.cpp_highlighter.setDocument(self.text_edit.document())
            self.cpp_highlighter_replaced.setDocument(self.text_edit_replaced.document())

        else:
            self.plain_text_highlighter.setDocument(self.text_edit.document())
            self.plain_text_highlighter_replaced.setDocument(self.text_edit_replaced.document())


    def delete_snippet(self):
        if self.current_snippet_file:
            try:
                os.remove(self.current_snippet_file)
                self.load_snippets()
                self.title_lineedit.clear()
                self.type_combobox.setCurrentIndex(0)
                self.text_edit.clear()
                self.update_input_layout()
                self.current_snippet_file = None

                index = self.model.index(0, 0)
                self.select_tree_item(index)
                self.on_tree_item_clicked(index)
                
            except Exception as e:
                print(f"Error deleting snippet: {e}")
        else:
            print("No snippet is currently selected.")

    def add_snippet(self):
        new_title = "New Snippet"
        new_type = "Plain text"
        new_content = ""

        # 获取当前时间作为创建时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_snippet = {
            'type': new_type,
            'title': new_title,
            'content': new_content,
            'created_time': now
        }

        # 生成以snippet开头加上时间戳的文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        file_name = f"snippet_{timestamp}.json"
        file_path = os.path.join(self.data_dir, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_snippet, f, ensure_ascii=False, indent=4)
            self.load_snippets()
            # 根据 created_time 匹配新添加的代码片段
            for i in range(self.model.rowCount()):
                created_time_item = self.model.item(i, 2)
                if created_time_item.text() == now:
                    index = self.model.index(i, 0)
                    self.select_tree_item(index)
                    self.on_tree_item_clicked(index)
                    break
        except Exception as e:
            print(f"Error adding snippet: {e}")

    def select_tree_item(self, index):
        start_index = self.model.index(index.row(), 0)
        end_index = self.model.index(index.row(), self.model.columnCount() - 1)
        selection = QItemSelection(start_index, end_index)
        self.tree_view.selectionModel().select(selection, QItemSelectionModel.SelectCurrent)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
