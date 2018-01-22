## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import _lib
from . import edit
from . import menu
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import json
import os


class MemoBase(QtWidgets.QWidget):

    def __init__(self, parent, data=None):
        if data is None:
            self._draw_data = []
        else:
            self._draw_data = data

        self.parent = parent
        super(MemoBase, self).__init__(self.parent)
        self.setup()

    def setup(self):
        _layout = self._get_layout()
        self.delete_memo_widget()
        _layout.addWidget(self)
        self.setObjectName(self.OJB_NAME)

    def _get_layout(self):
        for _c in self.parent.children():
            if _c.objectName() == self.LAYOUT_NAME:
                return _c
        #make new layout
        _layout = QtWidgets.QHBoxLayout(self.parent)
        _layout.setContentsMargins(0, 0, 0, 0)
        self.parent.setLayout(_layout)
        _layout.setObjectName(self.LAYOUT_NAME)
        return _layout

    def delete_memo_widget(self, *args):
        for _c in self.parent.children():
            if _c.objectName() == self.OJB_NAME:
                _c.deleteLater()


class AnimCurveEditorMemo(MemoBase):
    OJB_NAME = 'AnimMemoWidgetaaaaaa'
    LAYOUT_NAME = 'AnimMemoLayoutaaaaaaaa'

    def __init__(self, data=None):
        _p = _lib.get_anim_curve_editor_wiget()
        if _p is None:
            return
        super(AnimCurveEditorMemo, self).__init__(_p, data)

    def paintEvent(self, event):
        self._draw_timeline_memo()

    def _draw_timeline_memo(self):
        lines = _lib.draw_data_to_multi_line_data(self._draw_data)
        for i, line in enumerate(lines):
            for l in line:
                self._draw_single(l['fr'], l['bg_color'], i, len(lines))

    def _draw_single(self, fr, bg_color, line_number, line_count):
        _timeline_height = 26
        _single_height = _timeline_height / line_count

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
        _c = QtGui.QColor(bg_color)
        _c.setAlpha(128)
        painter.setBrush(_c)
        _pos, _w = self._get_draw_position_width(fr)
        _h = (_single_height + 1) * line_number

        painter.drawRect(_pos, _h + 50, _w, _single_height)

        color = QtGui.QColor('#000000')
        pen = QtGui.QPen(color, 28)
        painter.setPen(pen)

        _p = QtCore.QPoint(_pos, 15)
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


class AnimMemo(MemoBase):
    URL = "https://github.com/mochio326/AnimMemo"
    VAR = '0.0.1'
    OJB_NAME = 'AnimMemoWidget'
    LAYOUT_NAME = 'AnimMemoLayout'
    EXTENSION = 'animmemo'
    FILE_INFO = 'AnimMemoDrawData'

    @property
    def samename_file_path(self):
        _path = cmds.file(q=True, sn=True)
        if _path == '':
            return ''
        return _path.split('.')[0] + '.' + self.EXTENSION

    @property
    def draw_data_json_dump(self):
        text = json.dumps(self._draw_data, sort_keys=True, ensure_ascii=False, indent=2)
        return text

    def __init__(self, data=None):
        _p = _lib.get_timeline_wiget()
        super(AnimMemo, self).__init__(_p, data)
        self.callback = []
        self.change_time_range = False
        self.def_time_range_min = None
        self.def_time_range_max = None

        self.setMouseTracking(True)
        cmds.scriptJob(event=['timeChanged', self._view_message])
        cmds.scriptJob(cc=['playingBack', self._view_message])

        menu.TimeSliderMenu(self)
        self.add_callback()

    def _delete_script_job(self):
        jobs = cmds.scriptJob(listJobs=True)
        for _j in jobs:
            if 'AnimMemo._view_message' in _j:
                job_num = _j.split(':')[0]
                cmds.scriptJob(kill=int(job_num), force=True)

    def new_memo(self, *args):
        _result, _comment, _fr, _color = edit.EditMemoDialog.gui(fr=_lib.get_timeline_renge())
        if _result is False:
            return
        _dict = {'comment': _comment, 'fr': _fr, 'bg_color': _color}
        self._draw_data.append(_dict)
        self._draw_timeline_memo()
        self.repaint()

    def export_data(self, *args):
        _path = QtWidgets.QFileDialog.getSaveFileName(self, 'ExportFile', 'Result.{0}'.format(self.EXTENSION),
                                                      filter='{0} (*.{0})'.format(self.EXTENSION))
        _path = _path[0]
        self._export_file(_path)

    def export_data_samename_file(self, *args):
        _path = self.samename_file_path
        self._export_file(_path)

    def import_data(self, *args):
        _path = QtWidgets.QFileDialog.getOpenFileName(self, 'ImportFile', 'Result.{0}'.format(self.EXTENSION),
                                                      filter='{0} (*.{0})'.format(self.EXTENSION))
        _path = _path[0]
        self._file_to_import(_path)

    def import_data_samename_file(self, *args):
        _path = self.samename_file_path
        self._file_to_import(_path)

    def _file_to_import(self, path):
        if path == '':
            return
        with open(path) as fh:
            self._draw_data = json.loads(fh.read(), 'utf-8')
        self._draw_timeline_memo()
        self.repaint()

    def _export_file(self, path):
        if path == '':
            return
        with open(path, "w") as fh:
            fh.write(self.draw_data_json_dump.encode('utf-8'))

    def delete_all_memo(self, *args):
        self._draw_data = []
        self._draw_timeline_memo()
        self.repaint()

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
        AnimCurveEditorMemo(self._draw_data)
        self._draw_timeline_memo()

    def _draw_timeline_memo(self):
        lines = _lib.draw_data_to_multi_line_data(self._draw_data)
        for i, line in enumerate(lines):
            for l in line:
                self._draw_single(l['fr'], l['bg_color'], i, len(lines))

    def _save_draw_data(self, *args):
        if menu.TimeSliderMenu.save_to_current_scene:
            cmds.fileInfo(self.FILE_INFO, self.draw_data_json_dump)
        else:
            cmds.fileInfo(rm=self.FILE_INFO)

    def _draw_single(self, fr, bg_color, line_number, line_count):
        _timeline_height = 26
        _single_height = _timeline_height / line_count

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
        _c = QtGui.QColor(bg_color)
        _c.setAlpha(128)
        painter.setBrush(_c)
        _pos, _w = self._get_draw_position_width(fr)
        _h = (_single_height + 1) * line_number

        painter.drawRect(_pos, _h, _w, _single_height)

        color = QtGui.QColor('#000000')
        pen = QtGui.QPen(color, 28)
        painter.setPen(pen)

        _p = QtCore.QPoint(_pos, 15)
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
        comment = self._get_position_to_data(event, 'comment')
        if len(comment) > 0:
            QtWidgets.QToolTip.showText(event.globalPos(), '\r\n'.join(comment), self, QtCore.QRect(0, 0, self.width(), 0))

    def mouseDoubleClickEvent(self, event):
        super(AnimMemo, self).mouseDoubleClickEvent(event)

        if self.change_time_range is True:
            #フレーム範囲を元に戻す
            cmds.playbackOptions(min=self.def_time_range_min, max=self.def_time_range_max)
            self.change_time_range = False
            self.def_time_range_min = None
            self.def_time_range_max = None
        else:
            #フレーム範囲をメモ範囲に合わせる
            fr = self._get_position_to_data(event, 'fr')
            if len(fr) == 0:
                return
            self.change_time_range = True
            self.def_time_range_min = cmds.playbackOptions(q=True, min=True)
            self.def_time_range_max = cmds.playbackOptions(q=True, max=True)
            cmds.playbackOptions(min=fr[0][0], max=fr[0][1])

    def deleteLater(self):
        #remove callback
        for _id in self.callback:
            OpenMaya.MMessage.removeCallback(_id)
        self._delete_script_job()
        QtWidgets.QWidget.deleteLater(self)

    def add_callback(self):
        _id1 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self.delete_all_memo)
        _id2 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self._open_scene_callback)
        _id3 = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeSave, self._save_draw_data)

        self.callback = [_id1, _id2, _id3]

    def _get_position_to_data(self, event, key):
        data = []
        x = event.pos().x()
        for _d in self._draw_data:
            _pos, _w = self._get_draw_position_width(_d['fr'])
            if _pos < x < _pos + _w:
                data.append(_d[key])
        return data

    def _open_scene_callback(self, *args):
        self.delete_all_memo()
        _data = None

        _finfo = cmds.fileInfo(self.FILE_INFO, q=True)
        if _finfo:
            print _finfo[0]
            _data = _finfo[0].replace('\\"', '"')
            _data = _data.replace('\\n', '').strip()
            self._draw_data = json.loads(_data)

        if menu.TimeSliderMenu.import_samename_file:
            _path = self.samename_file_path
            if os.path.isfile(_path):
                with open(_path) as fh:
                    self._draw_data = json.loads(fh.read(), 'utf-8')

        if _data is None:
            return

        print _data

        self._draw_data = json.loads(_data, 'utf-8')
        self._draw_timeline_memo()
        self.repaint()

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
