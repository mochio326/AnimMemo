## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
from . import _lib
from . import edit
from . import menu
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omu

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
        #2017以降だとこれを行わないと表示されなかった
        #self.setFixedWidth(self.parent.width())

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


class GraphEditorMemo(MemoBase):
    OJB_NAME = 'GraphEditorMemoWidget'
    LAYOUT_NAME = 'GraphEditorMemoLayout'

    def __init__(self, data=None):
        _p = _lib.get_anim_curve_editor_wiget()
        if _p is None:
            return
        super(GraphEditorMemo, self).__init__(_p, data)
        self.callback = []
        self._add_callback()

        #透過処理してみる…
        #palette = QtGui.QPalette()
        #palette.setColor(QtGui.QPalette.Background, QtGui.QColor(255, 255, 255, 0))
        #self.setPalette(palette)
        self.setAutoFillBackground(True)

        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        #self.setStyleSheet("QWidget { background-color: transparent }");
        self.show()


    def paintEvent(self, event):
        super(GraphEditorMemo, self).paintEvent(event)
        print 'paintEvent!!!!!!'
        self._draw_timeline_memo()


    def _draw_timeline_memo(self):

        self.mask_path = QtGui.QPainterPath()
        #path.addRoundedRect(self.rect(), 3, 3)

        lines = _lib.draw_data_to_multi_line_data(self._draw_data)
        for i, line in enumerate(lines):
            for l in line:
                self._draw_single(l['fr'], l['bg_color'], i, len(lines))

        region = QtGui.QRegion(self.mask_path.toFillPolygon().toPolygon())
        self.setMask(region)


    def _draw_single(self, fr, bg_color, line_number, line_count):
        self.TIMELINE_HEIGHT = 26
        _single_height = self.TIMELINE_HEIGHT / line_count

        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)

        painter = QtGui.QPainter(self)
        color = QtGui.QColor(255, 255, 255, 128)
        pen = QtGui.QPen(color)
        painter.setPen(pen)

        #font = QtGui.QFont()
        #font.setPointSize(10)
        #painter.setFont(font)


        _c = QtGui.QColor(bg_color)
        #_c.setAlpha(128)
        painter.setBrush(_c)
        _pos, _w = self._get_draw_position_width(fr)
        _h = (_single_height + 1) * line_number

        #self.setMask(QtGui.QRegion(QtCore.QRect(_pos, _h + 50, _w, _single_height), QtGui.QRegion.Rectangle))
        painter.drawRect(_pos, _h + 50, _w, _single_height)
        self.mask_path.addRect(_pos, _h + 50, _w, _single_height)

        '''
        color = QtGui.QColor('#000000')
        pen = QtGui.QPen(color, 28)
        painter.setPen(pen)

        _p = QtCore.QPoint(_pos, 15)
        #painter.drawText(_p, 'hogehoge')
        '''

    def _get_draw_position_width(self, fr):
        #幅から引くと何故かちょうど良くなるピクセル数
        _width_offset_px = 0
        frame_left, frame_right, value_buttom, value_top = self._get_print_viewport_bounds()
        _total = frame_right - frame_left
        #１フレーム分の幅
        frame_width = (self.width() - _width_offset_px) / _total
        position = frame_width * (fr[0] - frame_left)
        width = frame_width * (fr[1] - fr[0] + 1)
        return position, width

    def _get_print_viewport_bounds(self):
        info = omu.MGraphEditorInfo()
        leftSu = om.MScriptUtil(0.0)
        leftPtr = leftSu.asDoublePtr()
        rightSu = om.MScriptUtil(0.0)
        rightPtr = rightSu.asDoublePtr()
        bottomSu = om.MScriptUtil(0.0)
        bottomPtr = bottomSu.asDoublePtr()
        topSu = om.MScriptUtil(0.0)
        topPtr = topSu.asDoublePtr()
        info.getViewportBounds(leftPtr, rightPtr, bottomPtr, topPtr)
        frame_left = om.MScriptUtil(leftPtr).asDouble()
        frame_right = om.MScriptUtil(rightPtr).asDouble()
        value_buttom = om.MScriptUtil(bottomPtr).asDouble()
        value_top =om.MScriptUtil(topPtr).asDouble()

        return frame_left, frame_right, value_buttom, value_top


    def _add_callback(self):
        _id1 = om.MEventMessage.addEventCallback('graphEditorChanged', self.paintEvent)
        self.callback = [_id1]

    def deleteLater(self):
        #remove callback
        for _id in self.callback:
            om.MMessage.removeCallback(_id)
        QtWidgets.QWidget.deleteLater(self)


class AnimMemo(MemoBase):
    URL = "https://github.com/mochio326/AnimMemo"
    VAR = '0.0.1'
    OJB_NAME = 'AnimMemoWidget'
    LAYOUT_NAME = 'AnimMemoLayout'
    EXTENSION = 'animmemo'
    FILE_INFO = 'AnimMemoDrawData'
    TIMELINE_HEIGHT = 26

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
        self._add_script_jobs()
        menu.TimeSliderMenu(self)
        self._add_callback()
        self.show()

    def new_memo(self, *args):
        _result, _comment, _fr, _color = edit.NewMemoDialog.gui(
            _lib.get_timeline_wiget(), fr=_lib.get_timeline_renge())
        if _result is False:
            return
        _dict = {'comment': _comment, 'fr': _fr, 'bg_color': _color}
        self._draw_data.append(_dict)
        self._draw_timeline_memo()
        self.repaint()

    def edit_memo(self, *args):
        if self._draw_data == []:
            return
        _result, _draw_data = edit.EditMemoDialog.gui(
            _lib.get_timeline_wiget(), draw_data=self._draw_data)
        if _result is False:
            return
        self._draw_data = _draw_data
        self._draw_timeline_memo()
        self.repaint()

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
                #format文だとなぜか上手くいかなかった <br>で改行しようとしたら枠からずれた…
                comment += '<font color="'+_d['bg_color']+'">'+_d['comment']+'</font>'
        if comment != '':
            cmds.inViewMessage(amg=comment, pos='midCenter', fade=True)
        else:
            cmds.inViewMessage(clear='midCenter')

    def _draw_timeline_memo(self):
        lines = _lib.draw_data_to_multi_line_data(self._draw_data)
        self.draw_line_count = len(lines)
        for i, line in enumerate(lines):
            for l in line:
                self._draw_single(l['fr'], l['bg_color'], i)

    def _draw_single(self, fr, bg_color, line_number):
        _single_height = self.TIMELINE_HEIGHT / self.draw_line_count

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

    def _get_position_to_data(self, event, key):
        # マウスの位置からアクティブなメモを取得
        data = []
        x = event.pos().x()
        for _d in self._draw_data:
            _pos, _w = self._get_draw_position_width(_d['fr'])
            if _pos < x < _pos + _w:
                data.append(_d[key])
        return data

    # -----------------------
    # DataSaveLoad
    # -----------------------
    def export_data_samename_file(self, *args):
        _path = self.samename_file_path
        self.export_file(_path)

    def import_data_samename_file(self, *args):
        _path = self.samename_file_path
        self.file_to_import(_path)

    def file_to_import(self, path):
        if path == '':
            return
        with open(path) as fh:
            self._draw_data = json.loads(fh.read(), 'utf-8')
        self._draw_timeline_memo()
        self.repaint()

    def export_file(self, path):
        if path == '':
            return
        with open(path, "w") as fh:
            fh.write(self.draw_data_json_dump.encode('utf-8'))

    def _save_draw_data_to_current_scene(self, *args):
        if menu.TimeSliderMenu.save_to_current_scene:
            cmds.fileInfo(self.FILE_INFO, self.draw_data_json_dump)
        else:
            cmds.fileInfo(rm=self.FILE_INFO)

    # -----------------------
    # QtFunctionOverride
    # -----------------------
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
            om.MMessage.removeCallback(_id)
        self._delete_script_jobs()
        QtWidgets.QWidget.deleteLater(self)

    def paintEvent(self, event):
        super(AnimMemo, self).paintEvent(event)
        #GraphEditorMemo(self._draw_data)
        self._draw_timeline_memo()

    # -----------------------
    # Callback ScriptJobs
    # -----------------------
    def _add_script_jobs(self):
        cmds.scriptJob(event=['timeChanged', self._view_message])
        cmds.scriptJob(cc=['playingBack', self._view_message])
        
    def _delete_script_jobs(self):
        jobs = cmds.scriptJob(listJobs=True)
        for _j in jobs:
            if 'AnimMemo._view_message' in _j:
                job_num = _j.split(':')[0]
                cmds.scriptJob(kill=int(job_num), force=True)

    def _add_callback(self):
        _id1 = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, self.delete_all_memo)
        _id2 = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, self._open_scene_callback)
        _id3 = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, self._save_draw_data_to_current_scene)
        self.callback = [_id1, _id2, _id3]

    def _open_scene_callback(self, *args):
        self.delete_all_memo()
        _data = None

        # シーン内に保持されているデータの読み込み
        _finfo = cmds.fileInfo(self.FILE_INFO, q=True)
        if _finfo:
            print _finfo[0]
            _data = _finfo[0].replace('\\"', '"')
            _data = _data.replace('\\n', '').strip()
            self._draw_data = json.loads(_data)
        # シーン同名ファイル読み込み
        if menu.TimeSliderMenu.import_samename_file:
            _path = self.samename_file_path
            if os.path.isfile(_path):
                with open(_path) as fh:
                    self._draw_data = json.loads(fh.read(), 'utf-8')

        if _data is None:
            return
        self._draw_data = json.loads(_data, 'utf-8')
        self._draw_timeline_memo()
        self.repaint()

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
