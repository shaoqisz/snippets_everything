import sys
import re
import os
import json
import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QCheckBox, QHeaderView, QLabel, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QStandardItemModel, QStandardItem, QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QSettings, QRegularExpression, QSortFilterProxyModel, QModelIndex, QMimeData, QTimer


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


class RecursiveFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        for column in range(self.sourceModel().columnCount(source_parent)):
            sub_index = self.sourceModel().index(source_row, column, source_parent)
            text = self.sourceModel().data(sub_index, Qt.DisplayRole)
            if text is not None:
                regExp = self.filterRegExp().pattern()
                if regExp:
                    try:
                        if re.search(regExp, str(text)):
                            return True
                    except re.error:
                        pass
                else:
                    regularExp = self.filterRegularExpression()
                    if regularExp.match(str(text)).hasMatch():
                        return True

        index = self.sourceModel().index(source_row, 0, parent=source_parent)
        rows = self.sourceModel().rowCount(index)
        for row in range(rows):
            if self.filterAcceptsRow(row, index):
                return True

        return super().filterAcceptsRow(source_row, source_parent)


def count_leading_spaces(line):
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        elif char == '\t':
            count += 4
        else:
            break
    return count


def remove_leading_spaces(line, remove_count):
    current_count = 0
    index = 0
    while current_count < remove_count and index < len(line):
        if line[index] == ' ':
            current_count += 1
        elif line[index] == '\t':
            current_count += 4
        index += 1
    return line[index:]


class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            self.insertPlainText(text)

    def keyPressEvent(self, event: QKeyEvent):
        # print(f'event.key()={event.key()}')
        cursor = self.textCursor()
        spaces = ' ' * 4

        if event.key() == Qt.Key_Backtab:
            print(f'shift+tab')
            if cursor.hasSelection():
                start_position = cursor.selectionStart()
                end_position = cursor.selectionEnd()
                selected_text = cursor.selectedText()
                lines = re.split(r'[\n\u2029]', selected_text)
                new_lines = []
                for line in lines:
                    space_count = count_leading_spaces(line)
                    if space_count >= 4:
                        new_lines.append(remove_leading_spaces(line, 4))
                    elif space_count > 0:
                        new_lines.append(line.lstrip(' \t'))
                    else:
                        new_lines.append(line)
                new_text = '\n'.join(new_lines)
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(new_text)
                new_cursor = self.textCursor()
                new_cursor.setPosition(start_position)
                new_cursor.setPosition(end_position - (len(selected_text) - len(new_text)),
                                        new_cursor.KeepAnchor)
                self.setTextCursor(new_cursor)
                cursor.endEditBlock()
            else:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.StartOfLine)
                line_text = cursor.block().text()
                space_count = count_leading_spaces(line_text)
                if space_count >= 4:
                    new_text = remove_leading_spaces(line_text, 4)
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    cursor.insertText(new_text)
                elif space_count > 0:
                    new_text = line_text.lstrip(' \t')
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    cursor.insertText(new_text)

        elif event.key() == Qt.Key_Tab: 
            if cursor.hasSelection():
                start_position = cursor.selectionStart()  # 记录选中区域起始位置
                end_position = cursor.selectionEnd()  # 记录选中区域结束位置
                # print(f'text={repr(self.toPlainText())}')

                selected_text = cursor.selectedText()
                # print(f'selected_text={selected_text}')
                # lines = selected_text.split('\n')
                lines = re.split(r'[\n\u2029]', selected_text)
                # print(f'lines={lines}')
                # 定义要添加的空格数量，这里设为 4 个
                new_text = '\n'.join([spaces + line for line in lines])
                print(f'new_text={new_text}')
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(new_text)
                cursor.endEditBlock()

                # 重新设置光标位置和选中区域
                new_cursor = self.textCursor()
                new_cursor.setPosition(start_position)
                new_cursor.setPosition(end_position + len(new_text) - len(selected_text),
                                    new_cursor.KeepAnchor)
                self.setTextCursor(new_cursor)
            else:
                cursor.insertText(spaces)
        else:
            super().keyPressEvent(event)

class MySearchComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.history = []
        self.history_file = "search_history_tree_view.txt"

        self.setEditable(True)
        self.load_history()
        self.setCurrentText('')
    
    def on_save_text(self):
        keyword = self.currentText().strip()
        if not keyword:
            return

        self.update_history(keyword)

        
    def update_history(self, keyword):
        print(f'update_history keyward={keyword}')

        if keyword in self.history:
            self.history.remove(keyword)
            
        # 插入到列表开头
        self.history.insert(0, keyword)
        
        # 限制历史记录数量
        if len(self.history) > 100:
            self.history = self.history[:100]
            
        # 更新下拉列表
        self.clear()
        self.addItems(self.history)
        
        # 保存到文件
        self.save_history()

        self.setCurrentIndex(0)

    def save_history(self):
        # print(f'save_history')
        with open(self.history_file, "w", encoding="utf-8") as f:
            for item in self.history:
                f.write(f"{item}\n")

    def load_history(self):
        # print(f'load_history')
        """从文件加载历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]
                # 去重处理并保留顺序
                seen = set()
                self.history = []
                for line in lines:
                    if line and line not in seen:
                        seen.add(line)
                        self.history.append(line)
                self.addItems(self.history)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.input_widgets = {}


        # 添加搜索框
        self.add_button = QPushButton("+")
        self.add_button.setMaximumWidth(40)
        self.delete_button = QPushButton("-")
        self.delete_button.setMaximumWidth(40)

        self.search_box = MySearchComboBox(self)
        self.search_box.setPlaceholderText("Search in tree")
        self.search_box.currentTextChanged.connect(self.filter_tree_view_slot)

        self.save_search_btn = QPushButton('Save Keywords')
        self.save_search_btn.clicked.connect(self.search_box.on_save_text)
        self.save_search_btn.setMaximumWidth(110)
        self.save_search_btn.setMaximumHeight(110)

        self.regex_cache = {}

        self.regex_check_box = QCheckBox('Regex')
        self.regex_check_box.setCheckState(Qt.CheckState.Unchecked)
        self.regex_check_box.setMaximumWidth(60)
        self.regex_check_box.setMaximumHeight(110)
        
        self.search_widget = QWidget()
        self.search_widget.setLayout(QGridLayout())
        self.search_widget.layout().addWidget(self.add_button, 0, 0)
        self.search_widget.layout().addWidget(self.delete_button, 0, 1)
        self.search_widget.layout().addWidget(self.search_box, 0, 2)
        self.search_widget.layout().addWidget(self.regex_check_box, 0, 3)
        self.search_widget.layout().addWidget(self.save_search_btn, 0, 4)
        self.search_widget.layout().setContentsMargins(0, 0, 0, 0)


        self.hor_splitter = QSplitter(Qt.Horizontal)
        self.hor_splitter.setObjectName("hor_splitter")

        self.content_loaded_from_json = None
        self.title_loaded_from_json = None
        self.placeholder_dict_loaded_from_json = None
        self.content_type_loaded_from_json = None

        # 左侧 TreeView
        self.tree = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['Title', 'Type', 'Created Time'])

        self.proxy_model = RecursiveFilterProxyModel()
        self.proxy_model.setSourceModel(self.tree_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写

        self.tree.setModel(self.proxy_model)
        self.tree.setEditTriggers(QTreeView.NoEditTriggers)  # 不允许修改内容
        self.tree.setSelectionMode(QTreeView.SingleSelection)  # 设置选择模式为单选
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.tree.clicked.connect(self.on_tree_item_clicked)
        self.tree.selectionModel().selectionChanged.connect(self.on_selection_changed)


        widget_with_tree_search = QWidget()
        widget_with_tree_search.setLayout(QVBoxLayout())
        widget_with_tree_search.layout().addWidget(self.search_widget)
        widget_with_tree_search.layout().addWidget(self.tree)
        widget_with_tree_search.layout().setContentsMargins(0,0,0,0)
        
        self.hor_splitter.addWidget(widget_with_tree_search)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0,0,0,0)

        # 显示 title 和 type 的控件
        info_layout = QHBoxLayout()
        self.title_lineedit = QLineEdit()
        self.title_lineedit.textChanged.connect(self.title_changed_slot)
        # 允许 title_lineedit 被修改
        self.title_lineedit.setReadOnly(False)
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(['Plain text', 'Python', 'C++'])
        self.type_combobox.currentTextChanged.connect(self.apply_highlighter)

        info_layout.addWidget(self.title_lineedit)
        info_layout.addWidget(self.type_combobox)

        right_layout.addLayout(info_layout)

        self.input_layout = QVBoxLayout()
        self.input_layout.setContentsMargins(0,0,0,0)
        self.input_layout.setSpacing(2)
        right_layout.addLayout(self.input_layout)


        self.text_edit = PlainTextEdit()
        self.text_edit_replaced = QTextEdit()
        self.text_edit_replaced.setReadOnly(True)

        self.python_highlighter = PythonHighlighter(self.text_edit.document())
        self.cpp_highlighter = CppHighlighter(self.text_edit.document())
        self.plain_text_highlighter = PlainTextHighlighter(self.text_edit.document())

        self.python_highlighter_replaced = PythonHighlighter(self.text_edit_replaced.document())
        self.cpp_highlighter_replaced = CppHighlighter(self.text_edit_replaced.document())
        self.plain_text_highlighter_replaced = PlainTextHighlighter(self.text_edit_replaced.document())

        self.text_edit.textChanged.connect(self.text_edit_changed)

        self.right_vert_splitter = QSplitter(Qt.Vertical, self)
        self.right_vert_splitter.setObjectName("right_vert_splitter")

        self.right_vert_splitter.addWidget(self.text_edit)
        self.right_vert_splitter.addWidget(self.text_edit_replaced)

        right_layout.addWidget(self.right_vert_splitter)

        # # 保留 replace 按钮
        # self.replace_button = QPushButton("Replace")
        # self.replace_button.clicked.connect(self.replace_placeholders)
        # right_layout.addWidget(self.replace_button)

        # self.save_button = QPushButton("Save")
        # self.save_button.clicked.connect(self.save_snippet)
        # right_layout.addWidget(self.save_button)

        self.interval_save_timer = QTimer()
        self.interval_save_timer.setInterval(2000)
        self.interval_save_timer.start()

        self.interval_save_timer.timeout.connect(self.save_snippet_changes)

        self.delete_button.clicked.connect(self.delete_snippet)
        self.add_button.clicked.connect(self.add_snippet)


        right_widget.setLayout(right_layout)
        self.hor_splitter.addWidget(right_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.hor_splitter)
        self.setLayout(main_layout)

        self.load_snippets()
        self.current_snippet_file = None

        index = self.tree_model.index(0, 0)
        self.select_tree_item(index)
        self.on_tree_item_clicked(index)

        app_name = 'Snippets Everything'
        self.setWindowTitle(app_name)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('pen.ico'))
        self.settings = QSettings("Philips", app_name)

        self.setWindowTitle(app_name)
        self.load_settings()

    def closeEvent(self, event):
        self.save_snippet()

        self.save_settings()
        event.accept()


    def save_settings(self):
        # geometry
        self.settings.setValue("geometry", self.saveGeometry())

        # splitter
        self.settings.setValue(self.hor_splitter.objectName(), self.hor_splitter.saveState())
        self.settings.setValue(self.right_vert_splitter.objectName(), self.right_vert_splitter.saveState())


    def load_settings(self):
        # geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # splitter
        splitter_state = self.settings.value(self.hor_splitter.objectName())
        if splitter_state:
            self.hor_splitter.restoreState(splitter_state)

        splitter_state = self.settings.value(self.right_vert_splitter.objectName())
        if splitter_state:
            self.right_vert_splitter.restoreState(splitter_state)


    def filter_tree_view_slot(self, text):
        if self.regex_check_box.isChecked():
            if text in self.regex_cache:
                regex = self.regex_cache[text]
            else:
                regex = QRegularExpression(text)
                self.regex_cache[text] = regex

            if regex.isValid():
                # print(f"set regex: '{text}'")
                self.proxy_model.setFilterRegularExpression(regex)
                self.tree.expandAll()
                return

        # print(f"set filter wildcard: '{text}'")
        self.proxy_model.setFilterRegularExpression(text)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        self.tree.expandAll()

    def load_snippets(self):
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['Title', 'Type', 'File', 'Timestamp'])
        self.tree.setColumnHidden(2, True) 
        # self.tree.setColumnHidden(3, True) 

        snippets = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        snippet['file_path'] = file_path
                        snippets.append(snippet)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        # 按创建时间排序
        snippets.sort(key=lambda x: x.get('timestamp', ''))
        for snippet in snippets:

            title = snippet.get('title', 'Unknown')
            title_item = QStandardItem(title)
            
            snippet_type = snippet.get('type', 'Unknown')
            type_item = QStandardItem(snippet_type)
            
            file_path = snippet.get('file_path', '')
            file_path_item = QStandardItem(file_path)

            timestamp = snippet.get('timestamp', '')
            timestamp_item = QStandardItem(timestamp)
            
            self.tree_model.appendRow([title_item, type_item, file_path_item, timestamp_item])

        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def on_selection_changed(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]
            self.handle_item_selection(index)

    def on_tree_item_clicked(self, index):
        self.handle_item_selection(index)

    def save_snippet_changes(self):
        changes = []
        if self.content_loaded_from_json and self.text_edit.toPlainText() != self.content_loaded_from_json:
            # print('content changed, need to save!!!')
            changes.append('content')
            self.save_snippet()
        # else:
        #     print('content not changed')

        if self.title_loaded_from_json and self.title_lineedit.text() != self.title_loaded_from_json:
            # print('title changed, need to save!!!')
            changes.append('title')
            self.save_snippet()
        # else:
        #     print('title not changed')

        if self.content_type_loaded_from_json and self.type_combobox.currentText() != self.content_type_loaded_from_json:
            # print('type_combobox changed, need to save!!!')
            changes.append('content type')
            self.save_snippet()
        # else:
            # print('type_combobox not changed')

        previous_values = {placeholder: input_field.text() for placeholder, input_field in self.input_widgets.items()}
        if self.placeholder_dict_loaded_from_json and previous_values != self.placeholder_dict_loaded_from_json:
            # print('placeholder_dict_loaded_from_json changed, need to save!!!')
            changes.append('placeholder')
            self.save_snippet()
        # else:
            # print('placeholder_dict_loaded_from_json not changed')
        if len(changes) > 0:
            print(f'changes={changes}')

    def get_items_1_2_3(self, item, index):
        item_column_1 = None
        item_column_2 = None
        item_column_3 = None

        if item:
            if index.column() == 0:  # 点击的是第一列
                item_column_1 = item
                parent_item = item.parent()
                if parent_item is None:
                    parent_item = self.tree_model.invisibleRootItem()

                item_column_2 = parent_item.child(item.row(), 1)
                item_column_3 = parent_item.child(item.row(), 2)

            elif index.column() == 1:  # 点击的是第二列
                item_column_2 = item
                parent_item = item.parent()
                if parent_item is None:
                    parent_item = self.tree_model.invisibleRootItem()
                item_column_1 = parent_item.child(item.row(), 0)
                item_column_3 = parent_item.child(item.row(), 2)

            elif index.column() == 2:  # 点击的是第三列
                item_column_3 = item
                parent_item = item.parent()
                if parent_item is None:
                    parent_item = self.tree_model.invisibleRootItem()
                item_column_1 = parent_item.child(item.row(), 0)
                item_column_2 = parent_item.child(item.row(), 1)

        return item_column_1, item_column_2, item_column_3
    
    def handle_item_selection(self, index):
        self.save_snippet_changes()

        item = self.tree_model.itemFromIndex(self.proxy_model.mapToSource(index))
        if item is None:
            return

        _, _, file_path_from_tree = self.get_items_1_2_3(item, index)
        if file_path_from_tree is None:
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:

                    with open(file_path, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        
                        if file_path == file_path_from_tree.text():
                            print(f'file_path={file_path}')

                            self.title_loaded_from_json = snippet.get('title', '')
                            self.title_lineedit.setText(self.title_loaded_from_json)

                            content_type = snippet.get('type', 'Plain text')
                            type_index = self.type_combobox.findText(content_type)
                            self.type_combobox.setCurrentIndex(type_index)

                            self.content_type_loaded_from_json = content_type
                            
                            self.content_loaded_from_json = snippet.get('content', '')
                            self.text_edit.setPlainText(self.content_loaded_from_json)


                            self.update_input_layout()
                            self.current_snippet_file = file_path
                            
                            self.apply_highlighter(content_type)

                            self.placeholder_dict_loaded_from_json = dict()
                            for placeholder, value in snippet.items():
                                if placeholder.startswith('$') and placeholder in self.input_widgets:
                                    # print(f'placeholder={placeholder} value={value}')
                                    self.input_widgets[placeholder].setText(value)
                                    self.placeholder_dict_loaded_from_json[placeholder] = value

                            self.replace_placeholders()
                            
                            break

                
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
    def update_input_layout(self):
        # print('update_input_layout')
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
            label = QLabel(placeholder)
            label.setStyleSheet('QLabel { color: red; font-weight: bold; padding: 5px; }')
            # label.setReadOnly(True)
            input_field = QLineEdit()
            input_field.textChanged.connect(self.input_field_changed)
            # 恢复之前输入框的值
            if placeholder in previous_values:
                input_field.setText(previous_values[placeholder])

            # print(f'placeholder={placeholder} input_field={input_field}')
            self.input_widgets[placeholder] = input_field

            hbox = QHBoxLayout()
            label.setMinimumWidth(150)
            label.setMaximumWidth(200)
            hbox.addWidget(label)
            hbox.addWidget(input_field)
            self.input_layout.addLayout(hbox)

        self.replace_placeholders()

    def text_edit_changed(self):
        self.update_input_layout()

    def title_changed_slot(self):
        pass

    def input_field_changed(self):
        # print('input_field_changed')
        self.replace_placeholders()

    def replace_placeholders(self):
        # print('replace_placeholders')
        code = self.text_edit.toPlainText()

        replaced_code = ''
        if self.type_combobox.currentText() == 'Plain text':
            for placeholder, input_field in self.input_widgets.items():
                replacement = input_field.text()
                if replacement:
                    code = code.replace(placeholder, f'<span style="color: black; font-weight: bold;">{replacement}</span>')

            replaced_code = (f'<p style="white-space: pre-wrap; color: green;">{code}</p>')
            self.text_edit_replaced.setHtml(replaced_code)
        else:
            for placeholder, input_field in self.input_widgets.items():
                replacement = input_field.text()
                if replacement:
                    code = code.replace(placeholder, replacement)
            replaced_code = code
            self.text_edit_replaced.setPlainText(replaced_code)

    def save_snippet(self):
        if not self.current_snippet_file:
            # print("No snippet is currently selected.")
            return
        
        title = self.title_lineedit.text()
        print(f'title={title} saved')
        snippet_type = self.type_combobox.currentText()
        content = self.text_edit.toPlainText()
        placeholders = re.findall(r'\$\w+', content)


        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        # 构建包含占位符值的字典
        placeholder_dict = {placeholder: self.input_widgets[placeholder].text() if placeholder in self.input_widgets else '' for placeholder in placeholders}

        snippet = {
            'type': snippet_type,
            'title': title,
            'content': content,
            'timestamp': timestamp,
            **placeholder_dict
        }

        try:
            with open(self.current_snippet_file, 'w', encoding='utf-8') as f:
                json.dump(snippet, f, ensure_ascii=False, indent=4)

            self.change_item(self.current_snippet_file, snippet_type, title, timestamp)
        
        except Exception as e:
            print(f"Error saving snippet: {e}")


    def change_item(self, file_path, snippet_type, title, timestamp):
        # 遍历 tree_model 的所有行
        for row in range(self.tree_model.rowCount()):
            # 获取当前行的 file_path 项
            file_path_item = self.tree_model.item(row, 2)
            if file_path_item and file_path_item.text() == file_path:
                # 修改 title 项
                title_item = self.tree_model.item(row, 0)
                if title_item:
                    title_item.setText(title)

                # 修改 snippet_type 项
                type_item = self.tree_model.item(row, 1)
                if type_item:
                    type_item.setText(snippet_type)

                # 修改 timestamp 项
                timestamp_item = self.tree_model.item(row, 3)
                if timestamp_item:
                    timestamp_item.setText(timestamp)
                break

    def add_item(self, file_path, snippet_type, title, timestamp):
        # 创建新的 QStandardItem 实例
        title_item = QStandardItem(title)
        type_item = QStandardItem(snippet_type)
        file_path_item = QStandardItem(file_path)
        timestamp_item = QStandardItem(timestamp)

        # 在 tree_model 中添加新行
        row = [title_item, type_item, file_path_item, timestamp_item]
        self.tree_model.appendRow(row)

        # 获取新添加项的索引
        index = self.tree_model.index(self.tree_model.rowCount() - 1, 0)

        return index

    def del_item(self, file_path):
        # 遍历 tree_model 的所有行
        for row in range(self.tree_model.rowCount()):
            # 获取当前行的 file_path 项
            file_path_item = self.tree_model.item(row, 2)
            if file_path_item and file_path_item.text() == file_path:
                # 删除匹配的行
                self.tree_model.removeRow(row)
                break

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
        reply = QMessageBox.question(self, 'Confirm Deletion', 'Are you sure you want to delete this item?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        
        if self.current_snippet_file:
            try:
                os.remove(self.current_snippet_file)
                self.del_item(self.current_snippet_file)
                
            except Exception as e:
                print(f"Error deleting snippet: {e}")
        else:
            print("No snippet is currently selected.")

    def add_snippet(self):
        new_title = "New Snippet"
        new_type = "Plain text"
        new_content = ""

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name_ts = now.strftime("%Y%m%d%H%M%S%f")
        file_name = f"snippet_{file_name_ts}.json"
        file_path = os.path.join(self.data_dir, file_name)

        new_snippet = {
            'type': new_type,
            'title': new_title,
            'content': new_content,
            'timestamp': timestamp
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_snippet, f, ensure_ascii=False, indent=4)

            index = self.add_item(file_path, new_type, new_title, timestamp)
            self.select_tree_item(index)
            self.on_tree_item_clicked(index)

        except Exception as e:
            print(f"Error adding snippet: {e}")

    def select_tree_item(self, index):
        start_index = self.tree_model.index(index.row(), 0)
        end_index = self.tree_model.index(index.row(), self.tree_model.columnCount() - 1)
        selection = QItemSelection(start_index, end_index)
        self.tree.selectionModel().select(selection, QItemSelectionModel.SelectCurrent)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
