


import re

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QShortcut, QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QAction, QCheckBox, QHeaderView, QLabel, QTreeView, QSplitter, QComboBox, QAbstractItemView
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QKeySequence, QStandardItemModel, QStandardItem, QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, QSettings, QRegularExpression, QSortFilterProxyModel, QModelIndex, QMimeData, QTimer


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


class TextEditOptimizedTab(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            self.insertPlainText(text)

    def keyPressEvent(self, event: QKeyEvent):
        cursor = self.textCursor()
        spaces = ' ' * 4
        if event.key() == Qt.Key_Backtab:
            scroll_value = self.verticalScrollBar().value()
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
                original_position = cursor.position()
                start_position = cursor.selectionStart()
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

                new_cursor = self.textCursor()
                new_cursor.setPosition(original_position-min(space_count, 4), QTextCursor.MoveAnchor)
                self.setTextCursor(new_cursor)

            self.verticalScrollBar().setValue(scroll_value)
        elif event.key() == Qt.Key_Tab:
            scroll_value = self.verticalScrollBar().value()
            if cursor.hasSelection():
                start_position = cursor.selectionStart()  # 记录选中区域起始位置
                end_position = cursor.selectionEnd()  # 记录选中区域结束位置
                selected_text = cursor.selectedText()
                lines = re.split(r'[\n\u2029]', selected_text)
                new_text = '\n'.join([spaces + line for line in lines])
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

            self.verticalScrollBar().setValue(scroll_value)
        else:
            super().keyPressEvent(event)