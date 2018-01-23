## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets

class EditMemoDialog(QtWidgets.QDialog):

    def __init__(self, parent, fr=None, color='#999999', mode='New', draw_data=None):
        super(EditMemoDialog, self).__init__(parent)
        self.color = color
        self._add_widgets(fr)
        self.mode = mode
        if draw_data is None:
            self.draw_data = []
        else:
            self.draw_data = draw_data
        self._layout()
        #self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle(self.mode + ' Memo')
        self.show()

    def _add_widgets(self, fr):
        self.le = QtWidgets.QTextEdit(self)
        self.fr_start = QtWidgets.QSpinBox(self)
        self.fr_end = QtWidgets.QSpinBox(self)
        self.fr_start.setFixedWidth(80)
        self.fr_end.setFixedWidth(80)
        if fr is not None:
            self.fr_start.setValue(fr[0])
            self.fr_end.setValue(fr[1])
        self.btn_color = QtWidgets.QPushButton(self)
        self.btn_color.setFixedSize(QtCore.QSize(300, 20))
        #self.btn_color.setSizePolicy(
        #    QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.view = QtWidgets.QTreeView()
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.view.setAlternatingRowColors(True)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['fr', 'bg_color', 'comment'])
        self.view.setModel(self.model)

        self.btn_color.clicked.connect(self._select_color)

    def _layout(self):
        horizontal_spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # ダイアログのOK/キャンセルボタンを用意
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)


        vb = QtWidgets.QVBoxLayout()

        hb = QtWidgets.QHBoxLayout()
        hb.addItem(horizontal_spacer_item)
        hb.addWidget(self.fr_start)
        hb.addWidget(QtWidgets.QLabel(u'～', self))
        hb.addWidget(self.fr_end)

        vb.addLayout(hb)
        vb.addWidget(self.le)
        vb.addWidget(self.btn_color)
        vb.addLayout(hb)
        self._set_button_color()

        vb.addWidget(btns)

        print self.mode
        if self.mode == 'New':
            self.setLayout(vb)
            return


        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(self.view)
        hb0.addLayout(vb)


        if hasattr(self.view.header(), 'setResizeMode'):
            # PySide
            self.view.header().setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.view.header().setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.view.header().setResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        else:
            # PySide2
            self.view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.view.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self.set_item()
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.view.customContextMenuRequested.connect(self._context)
        self.view.setAlternatingRowColors(True)


        self.setLayout(hb0)

    def set_item(self):
        index = 0
        for _d in self.draw_data:
            self.model.setItem(index, 0, QtGui.QStandardItem(str(_d['fr'][0]) + u'～' + str(_d['fr'][1]) + '  '))
            self.model.setItem(index, 1, QtGui.QStandardItem(_d['bg_color']))
            self.model.setItem(index, 2, QtGui.QStandardItem(_d['comment']))
            index += 1

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
    def gui(parent=None, fr=None, mode='New', draw_data=None):
        u"""ダイアログを開いてキャンバスサイズとOKキャンセルを返す."""
        dialog = EditMemoDialog(parent=parent, fr=fr, mode=mode, draw_data=draw_data)
        result = dialog.exec_()  # ダイアログを開く
        comment = dialog.get_comment()
        fr = dialog.get_fr()
        color = dialog.get_color()
        return result == QtWidgets.QDialog.Accepted, comment, fr, color

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
