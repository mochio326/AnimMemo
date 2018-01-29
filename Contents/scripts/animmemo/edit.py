## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets


class MemoDialogBase(QtWidgets.QDialog):

    def __init__(self, parent, fr=None, color='#999999'):
        super(MemoDialogBase, self).__init__(parent)
        self.horizontal_spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum)
        self.color = color
        self.fr = fr

    def _add_widgets(self):
        self.le = QtWidgets.QTextEdit(self)
        self.fr_start = QtWidgets.QSpinBox(self)
        self.fr_end = QtWidgets.QSpinBox(self)
        self.fr_start.setFixedWidth(80)
        self.fr_end.setFixedWidth(80)
        if self.fr is not None:
            self.fr_start.setValue(self.fr[0])
            self.fr_end.setValue(self.fr[1])
        self.btn_color = QtWidgets.QPushButton(self)
        self.btn_color.setFixedSize(QtCore.QSize(300, 20))
        #self.btn_color.setSizePolicy(
        #    QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.btn_color.clicked.connect(self._select_color)

    def _edit_layout(self):
        vb = QtWidgets.QVBoxLayout()

        hb = QtWidgets.QHBoxLayout()
        hb.addItem(self.horizontal_spacer_item)
        hb.addWidget(self.fr_start)
        hb.addWidget(QtWidgets.QLabel(u'～', self))
        hb.addWidget(self.fr_end)

        vb.addLayout(hb)
        vb.addWidget(self.le)
        vb.addWidget(self.btn_color)
        vb.addLayout(hb)
        self._set_button_color()

        return vb

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


class NewMemoDialog(MemoDialogBase):

    def __init__(self, parent, fr=None, color='#999999'):
        super(NewMemoDialog, self).__init__(parent, fr, color)
        self._add_widgets()
        self._layout()
        self.setWindowTitle('New Memo')
        self.show()

    def _layout(self):
        # ダイアログのOK/キャンセルボタンを用意
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        vb = self._edit_layout()
        vb.addWidget(btns)

        self.setLayout(vb)

    @staticmethod
    def gui(parent=None, fr=None):
        u"""ダイアログを開いてキャンバスサイズとOKキャンセルを返す."""
        dialog = NewMemoDialog(parent=parent, fr=fr)
        result = dialog.exec_()  # ダイアログを開く
        comment = dialog.get_comment()
        fr = dialog.get_fr()
        color = dialog.get_color()
        return result == QtWidgets.QDialog.Accepted, comment, fr, color


class EditMemoDialog(MemoDialogBase):

    def __init__(self, parent, draw_data=None):
        super(EditMemoDialog, self).__init__(parent)
        if draw_data is None:
            self.draw_data = []
        else:
            self.draw_data = draw_data
        self._add_widgets()
        self._layout()
        self.memo_list_view.setCurrentIndex(self.memo_list_model.index(0, 0))
        self.setWindowTitle('Edit Memo')
        self.show()

    def _add_widgets(self):
        super(EditMemoDialog, self)._add_widgets()
        self.memo_list_view = QtWidgets.QTreeView()
        self.memo_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.memo_list_view.setAlternatingRowColors(True)
        self.memo_list_model = QtGui.QStandardItemModel()
        self.memo_list_model.setHorizontalHeaderLabels(['frame', 'color', 'comment'])
        self.memo_list_view.setModel(self.memo_list_model)

        memo_list_sel_model = self.memo_list_view.selectionModel()
        memo_list_sel_model.selectionChanged.connect(self.memo_list_changed)

    def _layout(self):
        vb = self._edit_layout()

        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(self.memo_list_view)
        hb0.addLayout(vb)

        _hed = self.memo_list_view.header()
        _rtc = QtWidgets.QHeaderView.ResizeToContents
        if hasattr(_hed, 'setResizeMode'):
            [_hed.setResizeMode(i, _rtc) for i in range(3)]  # PySide
        else:
            [_hed.setSectionResizeMode(i, _rtc) for i in range(3)]  # PySide2

        self.set_list_item()
        self.memo_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.view.customContextMenuRequested.connect(self._context)
        self.memo_list_view.setAlternatingRowColors(True)


        # ダイアログのOK/キャンセルボタンを用意
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        vb0 = QtWidgets.QVBoxLayout()
        vb0.addLayout(hb0)
        vb0.addWidget(btns)
        self.setLayout(vb0)

    def memo_list_changed(self, selected, deselected):
        if len(deselected) != 0:
            _deselected_idx = deselected[0].indexes()[0].row()
            _selected_idx = selected[0].indexes()[0].row()
            #前回選択していたメモの内容を反映
            _comment = self.get_comment()
            _fr = self.get_fr()
            _color = self.get_color()
            _dict = {'comment': _comment, 'fr': _fr, 'bg_color': _color}
            self.draw_data[_deselected_idx] = _dict
            self.set_list_item()
            #選択状態を復元
            self.memo_list_view.setCurrentIndex(self.memo_list_model.index(_selected_idx, 0))
        self._apply_select_memo_data()

    def _apply_select_memo_data(self):

        _list_idx = self.memo_list_view.currentIndex()
        _d = self.draw_data[_list_idx.row()]

        self.le.setPlainText(_d['comment'])
        self.fr_start.setValue(_d['fr'][0])
        self.fr_end.setValue(_d['fr'][1])
        self.color = _d['bg_color']
        self._set_button_color()

    def set_list_item(self):
        index = 0
        for _d in self.draw_data:
            self.memo_list_model.setItem(index, 0, QtGui.QStandardItem(str(_d['fr'][0]) + u'～' + str(_d['fr'][1]) + '  '))
            self.memo_list_model.setItem(index, 1, QtGui.QStandardItem(_d['bg_color']))
            self.memo_list_model.setItem(index, 2, QtGui.QStandardItem(_d['comment']))
            index += 1

    @staticmethod
    def gui(parent=None, fr=None, mode='New', draw_data=None):
        u"""ダイアログを開いてキャンバスサイズとOKキャンセルを返す."""
        dialog = EditMemoDialog(parent=parent, draw_data=draw_data)
        result = dialog.exec_()  # ダイアログを開く
        _list_idx = dialog.memo_list_view.currentIndex()
        _d = {}
        _d['comment'] = dialog.get_comment()
        _d['fr'] = dialog.get_fr()
        _d['bg_color'] = dialog.get_color()
        dialog.draw_data[_list_idx.row()] = _d
        return result == QtWidgets.QDialog.Accepted, dialog.draw_data

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
