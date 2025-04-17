
import datetime

from PyQt5.QtWidgets import QLineEdit, QAction
# from PyQt5.QtGui import
# from PyQt5.QtCore import


class LineEditPasteDate(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def contextMenuEvent(self, event):
        # 创建默认的上下文菜单
        menu = self.createStandardContextMenu()

        menu.addSeparator()

        # 添加一个新的动作，用于粘贴当前日期
        paste_date_action = QAction("Paste Current Date", self)
        paste_date_action.triggered.connect(self.paste_current_date)
        menu.addAction(paste_date_action)

        # 在右键点击位置显示菜单
        menu.exec_(event.globalPos())

    def paste_current_date(self):
        current_date = datetime.datetime.now().strftime("%d-%b-%Y")
        self.insert(current_date)
