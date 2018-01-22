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


def get_anim_curve_editor():
    return cmds.animCurveEditor('graphEditor1GraphEd', q=True, control=True)


def get_play_back_slider():
    return mel.eval("$_=$gPlayBackSlider")


def get_timeline_wiget():
    _pbs = get_play_back_slider()
    _c = OpenMayaUI.MQtUtil.findControl(_pbs)
    w = shiboken.wrapInstance(long(_c), QtWidgets.QWidget)
    return w


def get_anim_curve_editor_wiget():
    _pbs = get_anim_curve_editor()
    _c = OpenMayaUI.MQtUtil.findControl(_pbs)
    if _c is None:
        return None
    w = shiboken.wrapInstance(long(_c), QtWidgets.QWidget)
    return w


def get_timeline_highlight_range():
    _pbs = get_play_back_slider()
    _r = cmds.timeControl(_pbs, q=True, ra=True)
    return _r[0], _r[1]


def get_timeline_renge():
    r = cmds.timeControl(get_play_back_slider(), query=True, ra=True)
    return [int(r[0]), int(r[1]) - 1]

def draw_data_to_multi_line_data(draw_data):
    lines = []
    for d in draw_data:
        _dfr = d['fr']
        _append = False
        for line in lines:
            _overlap = False
            for l in line:
                _lfr = l['fr']
                # 既存のデータのフレーム範囲に追加分のフレームが被っている
                if _lfr[0] <= _dfr[0] <= _lfr[1] or _lfr[0] <= _dfr[1] <= _lfr[1]:
                    _overlap = True
                    break
                # 追加分のフレーム範囲が既存のデータをすっぽり包んでいる
                if _dfr[0] <= _lfr[0] <= _dfr[1] and _dfr[0] <= _lfr[1] <= _dfr[1]:
                    _overlap = True
                    break

            if not _overlap:
                line.append(d)
                _append = True
                break

        # 新しい行追加
        if not _append:
            lines.append([d])

    return lines

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
