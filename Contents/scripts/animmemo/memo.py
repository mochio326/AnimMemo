## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya

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

    def __init__(self):
        self.data = []
        self.data.append({'fr': [3, 20], 'bg_color': [255, 0, 0], 'comment': u'もうちょっといい感じに緩急つける'})
        self.data.append({'fr': [15, 30], 'bg_color': [0, 0, 255], 'comment': u'バーンとしてドーンにする'})
        self.data.append({'fr': [50, 100], 'bg_color': [255, 255, 0], 'comment': u'いい感じ！問題なし！'})

        _p = _get_timeline_wiget()
        super(AnimMemo, self).__init__(_p)
        self.callback = []

        _layout = self._get_layout()
        self._delete_memo_wiget()

        _layout.addWidget(self)
        self.setMouseTracking(True)
        self.setObjectName(self.OJB_NAME)

        jobs = cmds.scriptJob(listJobs=True)
        for _j in jobs:
            if 'AnimMemo._view_message' in _j:
                job_num = _j.split(':')[0]
                cmds.scriptJob(kill=int(job_num), force=True)

        cmds.scriptJob(event=['timeChanged', self._view_message])
        cmds.scriptJob(cc=['playingBack', self._view_message])

        self.add_time_slider_menu()
        self.add_callback()

    def add_time_slider_menu(self):
        _original_menu = 'AnimMemoTimeSliderMenu'
        if not cmds.menuItem(_original_menu, q=True, ex=True):
            if maya_api_version() >= 201100:
                mel.eval('updateTimeSliderMenu TimeSliderMenu')

            _menu_name = 'TimeSliderMenu'
            cmds.menuItem(divider=True, p=_menu_name)
            cmds.menuItem(_original_menu, subMenu=True, label='AnimMemo Menu', p=_menu_name)
            cmds.menuItem(label='DeleteAll',
                          ann='Delete All Memo',
                          c=self._delete_memo_wiget)

    def _delete_memo_wiget(self, *args):
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
        for _d in self.data:
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
        for d in self.data:
            self._draw_timeline_memo(event, d['fr'], d['bg_color'])

    def _draw_timeline_memo(self, event, fr, bg_color):
        # スタイルシートを利用
        super(AnimMemo, self).paintEvent(event)
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
        QtWidgets.QWidget.deleteLater(self)

    def add_callback(self):
        _id1 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self._delete_memo_wiget)
        _id2 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self._delete_memo_wiget)
        self.callback = [_id1, _id2]

    def _get_position_to_comment(self, event):
        comment = ''
        x = event.pos().x()
        for _d in self.data:
            _pos, _w = self._get_draw_position_width(_d['fr'])
            if _pos < x < _pos + _w:
                if comment != '':
                    comment += '\r\n'
                comment += _d['comment']
        return comment

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

def main():
    AnimMemo()

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
