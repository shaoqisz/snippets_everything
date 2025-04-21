import sys
import re
import os
import json
import datetime
import markdown

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QShortcut, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QAction, QCheckBox, QHeaderView, QLabel, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QKeySequence, QStandardItemModel, QStandardItem, QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QSettings, QRegularExpression, QSortFilterProxyModel, QModelIndex, QMimeData, QTimer

from text_edit_search import TextEditSearch
from line_edit_past_date import LineEditPasteDate
from syntax_highlighter import PythonHighlighter, CppHighlighter, PlainTextHighlighter
from tree_view_proxy import RecursiveFilterProxyModel
from text_edit_optimized_tab import TextEditOptimizedTab
from search_box_history import SearchBoxHistory

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # 添加搜索框
        self.add_button = QPushButton("+")
        self.add_button.setMaximumWidth(40)
        self.delete_button = QPushButton("-")
        self.delete_button.setMaximumWidth(40)

        self.search_box = SearchBoxHistory(self)
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
        self.tree.setHorizontalScrollMode(QTreeView.ScrollPerPixel)  # 设置水平滚动策略
        self.tree.setAutoScroll(False)
        self.tree.setSortingEnabled(True)  # 启用排序功能
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['Title', 'Type', 'Created Time'])

        self.proxy_model = RecursiveFilterProxyModel()
        self.proxy_model.setSourceModel(self.tree_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写

        self.tree.setModel(self.proxy_model)
        self.tree.setEditTriggers(QTreeView.NoEditTriggers)  # 不允许修改内容
        self.tree.setSelectionMode(QTreeView.SingleSelection)  # 设置选择模式为单选
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # self.tree.clicked.connect(self.on_tree_item_clicked)
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
        self.type_combobox.addItems(['Plain text', 'Python', 'C++', 'Markdown'])
        self.type_combobox.currentTextChanged.connect(self.apply_highlighter)

        info_layout.addWidget(self.title_lineedit)
        info_layout.addWidget(self.type_combobox)

        right_layout.addLayout(info_layout)

        self.input_widgets = {}
        self.previous_placeholders = []
        self.input_layout = QGridLayout()
        self.input_layout.setContentsMargins(0,0,0,0)
        self.input_layout.setSpacing(2)
        right_layout.addLayout(self.input_layout)


        self.text_edit = TextEditOptimizedTab(self)
        font = QFont("Consolas")  # 或 "Courier New", "Menlo"
        font.setFixedPitch(True)  # 强制等宽
        self.text_edit.setFont(font)

        self.text_edit_search = TextEditSearch(self.text_edit)

        self.text_edit_replaced = QTextEdit(self)
        self.text_edit_replaced.setFont(font)
        self.text_edit_replaced.setReadOnly(True)
        self.text_edit_replaced_search = TextEditSearch(self.text_edit_replaced)


        self.python_highlighter = PythonHighlighter(self.text_edit.document())
        self.cpp_highlighter = CppHighlighter(self.text_edit.document())
        self.plain_text_highlighter = PlainTextHighlighter(self.text_edit.document())

        self.python_highlighter_replaced = PythonHighlighter(self.text_edit_replaced.document())
        self.cpp_highlighter_replaced = CppHighlighter(self.text_edit_replaced.document())
        self.plain_text_highlighter_replaced = PlainTextHighlighter(self.text_edit_replaced.document())

        self.text_edit.textChanged.connect(self.text_edit_changed)

        self.right_vert_splitter = QSplitter(Qt.Vertical, self)
        self.right_vert_splitter.setObjectName("right_vert_splitter")

        self.right_vert_splitter.addWidget(self.text_edit_search)
        self.right_vert_splitter.addWidget(self.text_edit_replaced_search)

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

        if self.proxy_model.rowCount() > 0:
            first_row_index = self.proxy_model.index(0, 0)
            self.select_tree_item_by_proxy_index(first_row_index)
            # self.handle_item_selection_by_proxy_index(first_row_index)

        self.shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut.activated.connect(self.set_focus_to_search_box)

        self.shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
        self.shortcut.activated.connect(self.set_focus_to_tree_view)

        self.shortcut = QShortcut(QKeySequence("Ctrl+2"), self)
        self.shortcut.activated.connect(self.set_focus_to_text_edit)


        app_name = 'Snippets Everything'
        self.setWindowTitle(app_name)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('pen.ico'))
        self.settings = QSettings("Philips", app_name)

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


        column_count = self.tree_model.columnCount()
        for col in range(column_count):
            width = self.tree.columnWidth(col)
            self.settings.setValue(f"tree_column_width/{col}", width)



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

        column_count = self.tree_model.columnCount()
        for col in range(column_count):
            width = self.settings.value(f"tree_column_width/{col}", defaultValue=100, type=int)
            self.tree.setColumnWidth(col, width)

    def set_focus_to_search_box(self):
        self.search_box.setFocus()

    def set_focus_to_tree_view(self):
        self.tree.setFocus()

    def set_focus_to_text_edit(self):
        self.text_edit.setFocus()

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

        # self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # self.tree.setColumnWidth(0, 250)

    def on_selection_changed(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]

            item = self.tree_model.itemFromIndex(self.proxy_model.mapToSource(index))
            if item is None:
                return
            _, _, file_path_from_tree = self.get_items_1_2_3(item, index)
            if file_path_from_tree is None:
                return
            self.handle_item_selection_by_file_path(file_path_from_tree)

    # def on_tree_item_clicked(self, index):
    #     item = self.tree_model.itemFromIndex(self.proxy_model.mapToSource(index))
    #     if item is None:
    #         return
    #     _, _, file_path_from_tree = self.get_items_1_2_3(item, index)
    #     if file_path_from_tree is None:
    #         return
    #     self.handle_item_selection_by_file_path(file_path_from_tree)

    def save_snippet_changes(self):
        changes = []
        if self.content_loaded_from_json is not None and self.text_edit.toPlainText() != self.content_loaded_from_json:
            # print('content changed, need to save!!!')
            changes.append('content')
            self.save_snippet()
            self.content_loaded_from_json = self.text_edit.toPlainText()
        # else:
        #     print(f'content_loaded_from_json={self.content_loaded_from_json}')
        #     print('content not changed')

        if self.title_loaded_from_json is not None and self.title_lineedit.text() != self.title_loaded_from_json:
            # print('title changed, need to save!!!')
            changes.append('title')
            self.save_snippet()
            self.title_loaded_from_json = self.title_lineedit.text()
        # else:
        #     print('title not changed')

        if self.content_type_loaded_from_json is not None and self.type_combobox.currentText() != self.content_type_loaded_from_json:
            # print('type_combobox changed, need to save!!!')
            changes.append('content type')
            self.save_snippet()
            self.content_type_loaded_from_json = self.type_combobox.currentText()
        # else:
            # print('type_combobox not changed')

        previous_values = {placeholder: input_field.text() for placeholder, input_field in self.input_widgets.items()}
        if self.placeholder_dict_loaded_from_json is not None and previous_values != self.placeholder_dict_loaded_from_json:
            # print('placeholder_dict_loaded_from_json changed, need to save!!!')
            changes.append('placeholder')
            self.save_snippet()
            self.placeholder_dict_loaded_from_json = previous_values
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
    
    def handle_item_selection_by_proxy_index(self, index):

        item = self.tree_model.itemFromIndex(self.proxy_model.mapToSource(index))
        if item is None:
            return

        _, _, file_path_from_tree = self.get_items_1_2_3(item, index)
        if file_path_from_tree is None:
            return

        self.handle_item_selection_by_file_path(file_path_from_tree)


    def handle_item_selection_by_file_path(self, file_path_from_tree):
        self.save_snippet_changes()

        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:

                    with open(file_path, 'r', encoding='utf-8') as f:
                        snippet = json.load(f)
                        
                        if file_path == file_path_from_tree.text():

                            self.title_loaded_from_json = snippet.get('title', '')
                            self.title_lineedit.setText(self.title_loaded_from_json)
                            print(f'select => {file_path} title={self.title_loaded_from_json}')

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

        code = self.text_edit.toPlainText()
        placeholders = re.findall(r'\$\w+', code)
        unique_placeholders = []
        for placeholder in placeholders:
            if placeholder not in unique_placeholders:
                unique_placeholders.append(placeholder)

        # 比较当前占位符和之前的占位符
        if unique_placeholders == self.previous_placeholders:
            # 占位符没有变化，恢复之前的值
            for placeholder, input_field in self.input_widgets.items():
                if placeholder in previous_values:
                    input_field.setText(previous_values[placeholder])
            self.replace_placeholders()
            return

        # 占位符有变化，更新布局
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

        self.input_layout.update()
        self.input_widgets = {}

        if unique_placeholders:
            for row, placeholder in enumerate(unique_placeholders):
                label = QLabel(placeholder)
                label.setStyleSheet('QLabel { color: magenta; font-weight: bold; padding: 5px; }')
                input_field = LineEditPasteDate()
                input_field.textChanged.connect(self.input_field_changed)
                # 恢复之前输入框的值
                if placeholder in previous_values:
                    input_field.setText(previous_values[placeholder])

                self.input_widgets[placeholder] = input_field

                self.input_layout.addWidget(label, row, 0)
                self.input_layout.addWidget(input_field, row, 1)

        self.previous_placeholders = unique_placeholders
        self.replace_placeholders()

    def text_edit_changed(self):
        self.update_input_layout()

    def title_changed_slot(self):
        pass

    def input_field_changed(self):
        # print('input_field_changed')
        self.replace_placeholders()

    def replace_placeholders_with_inputs(self, code, replacement_fmt=None):
        for placeholder, input_field in self.input_widgets.items():
            replacement = input_field.text()
            if replacement:
                if replacement_fmt is not None:
                    code = code.replace(placeholder, replacement_fmt.format(replacement))
                else:
                    code = code.replace(placeholder, replacement)
        return code

    def replace_placeholders(self):
        # print('replace_placeholders')
        code = self.text_edit.toPlainText()

        replaced_code = ''
        if self.type_combobox.currentText() == 'Plain text':
            replaced_code = self.replace_placeholders_with_inputs(code, '<span style="color: magenta; font-weight: bold;">{}</span>')
            html = (f'<p style="white-space: pre-wrap; color: green;">{replaced_code}</p>')
            self.text_edit_replaced.setHtml(html)

        elif self.type_combobox.currentText() == 'Markdown':
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Simple Code Highlighting with CSS</title>
                <style>
                    p code {
                        font-family: 'Courier New', Courier, monospace;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        padding: 2px 5px;
                        color: #c7254e;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }
                </style>
            </head>
                <body>
                    __replace__
                </body>
            </html>   
            """
            replaced_code = self.replace_placeholders_with_inputs(code)
            html_body = markdown.markdown(replaced_code)
            html = html.replace('__replace__', html_body)
            self.text_edit_replaced.setHtml(html)
        else:
            replaced_code = self.replace_placeholders_with_inputs(code)
            self.text_edit_replaced.setPlainText(replaced_code)

    def save_snippet(self):
        if not self.current_snippet_file:
            print("No snippet is currently selected.")
            return
        
        title = self.title_lineedit.text()
        print(f'title={title} saved')
        snippet_type = self.type_combobox.currentText()
        content = self.text_edit.toPlainText()
        placeholders = re.findall(r'\$\w+', content)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        # print(f'timestamp={timestamp}')
        timestamp = timestamp[:-3]

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
            
            print(f"save and update item => {self.current_snippet_file} title={title}")

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

        # 获取新添加项的源模型索引
        source_index = self.tree_model.index(self.tree_model.rowCount() - 1, 0)

        # 将源模型索引转换为代理模型索引
        proxy_index = self.proxy_model.mapFromSource(source_index)

        return proxy_index

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
        elif snippet_type == 'Plain text' or snippet_type == 'Markdown':
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
        # print(f'timestamp={timestamp}')
        timestamp = timestamp[:-3]
        
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

            proxy_index = self.add_item(file_path, new_type, new_title, timestamp)
            self.select_tree_item_by_proxy_index(proxy_index)
            # self.handle_item_selection_by_proxy_index(proxy_index)

        except Exception as e:
            print(f"Error adding snippet: {e}")

    # def select_tree_item_by_proxy(self, index):
    #     print(f'select_tree_item')
    #     # 将代理模型的索引转换为源模型的索引
    #     source_index = self.proxy_model.mapToSource(index)
    #     start_index = self.tree_model.index(source_index.row(), 0)
    #     end_index = self.tree_model.index(source_index.row(), self.tree_model.columnCount() - 1)
    #     selection = QItemSelection(start_index, end_index)
    #     # 将源模型的选择范围转换为代理模型的选择范围
    #     proxy_selection = QItemSelection()
    #     for range in selection:
    #         top_left_index = QModelIndex(range.topLeft())
    #         bottom_right_index = QModelIndex(range.bottomRight())
    #         proxy_top_left = self.proxy_model.mapFromSource(top_left_index)
    #         proxy_bottom_right = self.proxy_model.mapFromSource(bottom_right_index)
    #         proxy_selection.select(proxy_top_left, proxy_bottom_right)
    #     self.tree.selectionModel().select(proxy_selection, QItemSelectionModel.SelectCurrent)
    #     print(f'select_tree_item done')

    # def select_first_row(self):
    #     if self.proxy_model.rowCount() > 0:
    #         # 获取代理模型中第一行第一列的索引
    #         first_row_index = self.proxy_model.index(0, 0)
    #         self.select_tree_item(first_row_index)


    def select_tree_item_by_proxy_index(self, index):
        self.tree.selectionModel().clearSelection()
        start_index = self.proxy_model.index(index.row(), 0)
        end_index = self.proxy_model.index(index.row(), self.proxy_model.columnCount() - 1)
        selection = QItemSelection(start_index, end_index)
        self.tree.selectionModel().select(selection, QItemSelectionModel.SelectCurrent)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
