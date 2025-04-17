

import re

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QShortcut, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QAction, QCheckBox, QHeaderView, QLabel, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QKeySequence, QStandardItemModel, QStandardItem, QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QSettings, QRegularExpression, QSortFilterProxyModel, QModelIndex, QMimeData, QTimer


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
