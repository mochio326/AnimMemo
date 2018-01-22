## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets

class EditMemoDialog(QtWidgets.QDialog):

    def __init__(self, parent, fr=None, color='#999999'):
        super(EditMemoDialog, self).__init__(parent)
        self.color = color

        self.le = QtWidgets.QTextEdit(self)
        self.fr_start = QtWidgets.QSpinBox(self)
        self.fr_end = QtWidgets.QSpinBox(self)
        self.fr_start.setFixedWidth(80)
        self.fr_end.setFixedWidth(80)
        if fr is not None:
            self.fr_start.setValue(fr[0])
            self.fr_end.setValue(fr[1])
        self.btn_color = QtWidgets.QPushButton(self)

        horizontal_spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # ダイアログのOK/キャンセルボタンを用意
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        vb = QtWidgets.QVBoxLayout()

        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(QtWidgets.QLabel("Comment", self))
        hb.addWidget(self.le)
        vb.addLayout(hb)

        hb = QtWidgets.QHBoxLayout()
        hb.addItem(horizontal_spacer_item)
        hb.addWidget(self.fr_start)
        hb.addWidget(QtWidgets.QLabel(u'～', self))
        hb.addWidget(self.fr_end)
        vb.addLayout(hb)

        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(QtWidgets.QLabel("Color", self))
        hb.addWidget(self.btn_color)
        vb.addLayout(hb)
        self.btn_color.clicked.connect(self._select_color)
        self._set_button_color()

        vb.addWidget(btns)
        self.setLayout(vb)

        #self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('New Memo')
        self.show()

    def _select_color(self):
        color = QtWidgets.QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color.name()
            self._set_button_color()

    def _set_button_color(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(self.color))
        self.btn_color.setPalette(palette)

    def get_comment(self):
        return self.le.toPlainText()

    def get_fr(self):
        return [self.fr_start.value(), self.fr_end.value()]

    def get_color(self):
        return self.color

    @staticmethod
    def gui(parent=None, fr=None):
        u"""ダイアログを開いてキャンバスサイズとOKキャンセルを返す."""
        dialog = EditMemoDialog(parent, fr)
        result = dialog.exec_()  # ダイアログを開く
        comment = dialog.get_comment()
        fr = dialog.get_fr()
        color = dialog.get_color()
        return result == QtWidgets.QDialog.Accepted, comment, fr, color

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
