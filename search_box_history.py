
import os

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QShortcut, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QAction, QCheckBox, QHeaderView, QLabel, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QKeySequence, QStandardItemModel, QStandardItem, QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QSettings, QRegularExpression, QSortFilterProxyModel, QModelIndex, QMimeData, QTimer


class SearchBoxHistory(QComboBox):
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
