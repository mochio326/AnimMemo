## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
import json

def maya_api_version():
    return int(cmds.about(api=True))

if 201700 <= maya_api_version() and maya_api_version() < 201800:
    import shiboken2 as shiboken
else:
    import shiboken

class AnimMemo(QtWidgets.QWidget):
    URL = "https://github.com/mochio326/AnimMemo"
    VAR = '0.0.1'
    OJB_NAME = 'AnimMemoWidget'
    LAYOUT_NAME = 'AnimMemoLayout'

    def __init__(self, data=None):
        if data is None:
            self._draw_data = []
        else:
            self._draw_data = data
        _p = _get_timeline_wiget()
        super(AnimMemo, self).__init__(_p)
        self.callback = []

    def setup(self):
        _layout = self._get_layout()
        self.delete_memo_wiget()

        _layout.addWidget(self)
        self.setMouseTracking(True)
        self.setObjectName(self.OJB_NAME)

        cmds.scriptJob(event=['timeChanged', self._view_message])
        cmds.scriptJob(cc=['playingBack', self._view_message])

        self.add_time_slider_menu()
        self.add_callback()

    def _delete_script_job(self):
        jobs = cmds.scriptJob(listJobs=True)
        for _j in jobs:
            if 'AnimMemo._view_message' in _j:
                job_num = _j.split(':')[0]
                cmds.scriptJob(kill=int(job_num), force=True)

    def add_time_slider_menu(self):
        _original_menu = 'AnimMemoTimeSliderMenu'
        if cmds.menuItem(_original_menu, q=True, ex=True):
            return

        if maya_api_version() >= 201100:
            mel.eval('updateTimeSliderMenu TimeSliderMenu')

        _menu_name = 'TimeSliderMenu'
        cmds.menuItem(divider=True, p=_menu_name)

        cmds.menuItem(_original_menu, subMenu=True, label='AnimMemo Menu', p=_menu_name)

        cmds.menuItem(label='Create',
                      ann='Create Mew Memo',
                      c=self.new_memo)

        cmds.menuItem(divider=True, p=_original_menu)

        cmds.menuItem(label='DeleteAll',
                      ann='Delete All Memo',
                      c=self.delete_all_memo)

        cmds.menuItem(divider=True, p=_original_menu)

        cmds.menuItem(label='ExportFile',
                      ann='ExportFile',
                      c=self.export_data)

        cmds.menuItem(label='ImportFile',
                      ann='ImportFile',
                      c=self.import_data)

    def new_memo(self, *args):
        _result, _comment = NewMemo.gui()
        if _result is False:
            return
        _fr = _get_timeline_renge()
        _color = [128, 128, 128]
        _dict = {'comment':_comment, 'fr':_fr, 'bg_color':_color}
        self._draw_data.append(_dict)
        self._draw_timeline_memo()
        self.repaint()

    def export_data(self, *args):
        _path = QtWidgets.QFileDialog.getSaveFileName(self, "ExportFile", "Result.animmemo", filter="animmemo (*.animmemo)")
        _path = _path[0]
        if _path == '':
            return
        text = json.dumps(self._draw_data, sort_keys=True, ensure_ascii=False, indent=2)
        with open(_path, "w") as fh:
            fh.write(text.encode("utf-8"))

    def import_data(self, *args):
        _path = QtWidgets.QFileDialog.getOpenFileName(self, "ImportFile", "Result.animmemo", filter="animmemo (*.animmemo)")
        _path = _path[0]
        if _path == '':
            return
        with open(_path) as fh:
            self._draw_data = json.loads(fh.read(), "utf-8")
        self._draw_timeline_memo()
        self.repaint()

    def delete_all_memo(self, *args):
        self._draw_data = []
        self._draw_timeline_memo()
        self.repaint()

    def delete_memo_wiget(self, *args):
        _p = _get_timeline_wiget()
        for _c in _p.children():
            if _c.objectName() == self.OJB_NAME:
                _c.deleteLater()

    def _get_layout(self):
        _p = _get_timeline_wiget()
        for _c in _p.children():
            if _c.objectName() == self.LAYOUT_NAME:
                return _c
        #make new layout
        _layout = QtWidgets.QHBoxLayout(_p)
        _layout.setContentsMargins(0, 0, 0, 0)
        _p.setLayout(_layout)
        _layout.setObjectName(self.LAYOUT_NAME)
        return _layout

    def _view_message(self):
        _t = cmds.currentTime(q=True)
        comment = ''
        for _d in self._draw_data:
            _fr = _d['fr']
            if _fr[0] <= _t <= _fr[1]:
                if comment != '':
                    comment += '\r\n'
                comment += _d['comment']
        if comment != '':
            cmds.inViewMessage(amg=comment, pos='midCenter', fade=True)
        else:
            cmds.inViewMessage(clear='midCenter')

    def paintEvent(self, event):
        super(AnimMemo, self).paintEvent(event)
        self._draw_timeline_memo()

    def _draw_timeline_memo(self):
        for d in self._draw_data:
            self._draw_single( d['fr'], d['bg_color'])

    def _draw_single(self, fr, bg_color):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)

        painter = QtGui.QPainter(self)
        color = QtGui.QColor(255, 255, 255, 128)
        pen = QtGui.QPen(color)
        painter.setPen(pen)
        '''
        font = QtGui.QFont()
        font.setPointSize(10)
        painter.setFont(font)
        line = QtCore.QLine(
            QtCore.QPoint(frame_width * (fr - 1), 0),
            QtCore.QPoint(frame_width * fr, 28)
        )
        painter.drawLine(line)
        '''
        painter.setBrush(QtGui.QColor(bg_color[0], bg_color[1], bg_color[2], 128))
        _pos, _w = self._get_draw_position_width(fr)
        painter.drawRect(_pos, 10, _w, 10)

        color = QtGui.QColor('#000000')
        pen = QtGui.QPen(color, 28)
        painter.setPen(pen)

        _p = QtCore.QPoint(110, 15)
        #painter.drawText(_p, 'hogehoge')

    def _get_draw_position_width(self, fr):
        #幅から引くと何故かちょうど良くなるピクセル数
        _width_offset_px = 10
        _start = cmds.playbackOptions(q=True, min=True)
        _end = cmds.playbackOptions(q=True, max=True)
        _total = _end - _start + 1
        #１フレーム分の幅
        frame_width = (self.width() - _width_offset_px) / _total
        position = frame_width * (fr[0] - _start) + 6
        width = frame_width * (fr[1] - fr[0] + 1)
        return position, width

    def mouseMoveEvent(self, event):
        super(AnimMemo, self).mouseMoveEvent(event)
        comment = self._get_position_to_comment(event)
        if comment:
            QtWidgets.QToolTip.showText(event.globalPos(), comment, self, QtCore.QRect(0, 0, self.width(), 0))

    def deleteLater(self):
        #remove callback
        for _id in self.callback:
            OpenMaya.MMessage.removeCallback(_id)
        self._delete_script_job()
        QtWidgets.QWidget.deleteLater(self)

    def add_callback(self):
        _id1 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self.delete_all_memo)
        _id2 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self.delete_all_memo)
        self.callback = [_id1, _id2]

    def _get_position_to_comment(self, event):
        comment = ''
        x = event.pos().x()
        for _d in self._draw_data:
            _pos, _w = self._get_draw_position_width(_d['fr'])
            if _pos < x < _pos + _w:
                if comment != '':
                    comment += '\r\n'
                comment += _d['comment']
        return comment

class NewMemo(QtWidgets.QDialog):

    def __init__(self, parent):
        super(NewMemo, self).__init__(parent)

        self.le = QtWidgets.QTextEdit(self)
        self.fr_start = QtWidgets.QSpinBox(self)
        self.fr_end = QtWidgets.QSpinBox(self)
        self.fr_start.setFixedWidth(80)
        self.fr_end.setFixedWidth(80)

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

        vb.addWidget(btns)
        self.setLayout(vb)

        #self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('New Memo')
        self.show()

    def get_comment(self):
        return self.le.toPlainText()

    @staticmethod
    def gui(parent=None):
        u"""ダイアログを開いてキャンバスサイズとOKキャンセルを返す."""
        dialog = NewMemo(parent)
        result = dialog.exec_()  # ダイアログを開く
        comment = dialog.get_comment()
        print result == QtWidgets.QDialog.Accepted, comment
        return result == QtWidgets.QDialog.Accepted, comment

# #################################################################################################

def _get_play_back_slider():
    return mel.eval("$_=$gPlayBackSlider")

def _get_timeline_wiget():
    _pbs = _get_play_back_slider()
    _c = OpenMayaUI.MQtUtil.findControl(_pbs)
    w = shiboken.wrapInstance(long(_c), QtWidgets.QWidget)
    return w

def _get_timeline_highlight_range():
    _pbs = _get_play_back_slider()
    _r = cmds.timeControl(_pbs, q=True, ra=True)
    return _r[0], _r[1]

def _get_timeline_renge():
    r = cmds.timeControl(_get_play_back_slider(), query=True, ra=True)
    return [int(r[0]), int(r[1]) - 1]

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
