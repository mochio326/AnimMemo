## -*- coding: utf-8 -*-
from .vendor.Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
import json
import os


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
    OPTVER_IMPORT_SAMENAME_FILE = 'AnimMemo_Import_SameName_File'
    OPTVER_SAVE_TO_CURRENT_SCENE = 'AnimMemo_Save_to_CurrentScene'
    EXTENSION = 'animmemo'
    FILE_INFO = 'AnimMemoDrawData'

    @property
    def import_samename_file(self):
        _ex = cmds.optionVar(exists=self.OPTVER_IMPORT_SAMENAME_FILE)
        if not _ex:
            return True
        return cmds.optionVar(q=self.OPTVER_IMPORT_SAMENAME_FILE)

    @import_samename_file.setter
    def import_samename_file(self, val):
        cmds.optionVar(iv=[self.OPTVER_IMPORT_SAMENAME_FILE, val])

    @property
    def save_to_current_scene(self):
        _ex = cmds.optionVar(exists=self.OPTVER_SAVE_TO_CURRENT_SCENE)
        if not _ex:
            return False
        return cmds.optionVar(q=self.OPTVER_SAVE_TO_CURRENT_SCENE)

    @save_to_current_scene.setter
    def save_to_current_scene(self, val):
        cmds.optionVar(iv=[self.OPTVER_SAVE_TO_CURRENT_SCENE, val])

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
        if data is None:
            self._draw_data = []
        else:
            self._draw_data = data
        _p = _get_timeline_wiget()
        super(AnimMemo, self).__init__(_p)
        self.callback = []

        self.change_time_range = False
        self.def_time_range_min = None
        self.def_time_range_max = None

        self.setup()

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
        _option_menu = 'AnimMemoTimeSliderMenu_Option'

        if cmds.menuItem(_original_menu, q=True, ex=True):
            cmds.deleteUI(_original_menu, mi=True)

        if maya_api_version() >= 201100:
            mel.eval('updateTimeSliderMenu TimeSliderMenu')

        _menu_name = 'TimeSliderMenu'
        cmds.menuItem(divider=True, p=_menu_name)

        _m = cmds.menuItem(_original_menu, subMenu=True, label='AnimMemo Menu', p=_menu_name, to=True)

        cmds.menuItem(label='Create',
                      ann='Create Mew Memo',
                      c=self.new_memo,
                      p=_m)

        cmds.menuItem(divider=True, p=_original_menu)

        cmds.menuItem(label='DeleteAll',
                      ann='Delete All Memo',
                      c=self.delete_all_memo,
                      p=_m)

        cmds.menuItem(divider=True, p=_m)

        cmds.menuItem(label='ExportFile',
                      ann='ExportFile',
                      c=self.export_data,
                      p=_m)

        cmds.menuItem(label='ImportFile',
                      ann='ImportFile',
                      c=self.import_data,
                      p=_m)

        cmds.menuItem(divider=True, p=_m)

        cmds.menuItem(label='ExportFile(Scnes SameName File)',
                      ann='Export the same name file',
                      c=self.export_data_samename_file,
                      p=_m)

        cmds.menuItem(label='ImportFile(Scnes SameName File)',
                      ann='Import the same name file',
                      c=self.import_data_samename_file,
                      p=_m)

        _o = cmds.menuItem(_option_menu, subMenu=True, label='Option', p=_m)

        self.imp_smf = cmds.menuItem(label='Import SameName File',
                      checkBox=self.import_samename_file,
                      ann='Import the same name file when opening a scene',
                      c=self._change_option,
                      p=_o)

        self.save2scene = cmds.menuItem(label='Save to CurrentScene',
                      checkBox=self.save_to_current_scene,
                      ann='Save to CurrentScene',
                      c=self._change_option,
                      p=_o)

    def _change_option(self, *args):
        self.import_samename_file = cmds.menuItem(self.imp_smf, q=True, checkBox=True)
        self.save_to_current_scene = cmds.menuItem(self.save2scene, q=True, checkBox=True)

    def new_memo(self, *args):
        _result, _comment, _fr, _color = EditMemo.gui(fr=_get_timeline_renge())
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
            self._draw_single(d['fr'], d['bg_color'])

    def _save_draw_data(self, *args):
        if self.save_to_current_scene:
            cmds.fileInfo(self.FILE_INFO, self.draw_data_json_dump)
        else:
            cmds.fileInfo(rm=self.FILE_INFO)

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
        _c = QtGui.QColor(bg_color)
        _c.setAlpha(128)
        painter.setBrush(_c)
        _pos, _w = self._get_draw_position_width(fr)
        painter.drawRect(_pos, 10, _w, 10)

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

        if self.import_samename_file:
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


class EditMemo(QtWidgets.QDialog):

    def __init__(self, parent, fr=None, color='#999999'):
        super(EditMemo, self).__init__(parent)
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
        dialog = EditMemo(parent, fr)
        result = dialog.exec_()  # ダイアログを開く
        comment = dialog.get_comment()
        fr = dialog.get_fr()
        color = dialog.get_color()
        return result == QtWidgets.QDialog.Accepted, comment, fr, color

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
