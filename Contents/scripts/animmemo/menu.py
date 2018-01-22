## -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
from . import _lib

class TimeSliderMenu(object):
    OPTVER_IMPORT_SAMENAME_FILE = 'AnimMemo_Import_SameName_File'
    OPTVER_SAVE_TO_CURRENT_SCENE = 'AnimMemo_Save_to_CurrentScene'

    @property
    @classmethod
    def import_samename_file(cls):
        return cls.get_import_samename_file()

    @property
    @classmethod
    def save_to_current_scene(cls):
        return cls.get_save_to_current_scene()

    def __init__(self, instance):
        self.add_time_slider_menu(instance)

    def add_time_slider_menu(self, instance):
        _original_menu = 'AnimMemoTimeSliderMenu'
        _option_menu = 'AnimMemoTimeSliderMenu_Option'

        if cmds.menuItem(_original_menu, q=True, ex=True):
            cmds.deleteUI(_original_menu, mi=True)

        if _lib.maya_api_version() >= 201100:
            mel.eval('updateTimeSliderMenu TimeSliderMenu')

        _menu_name = 'TimeSliderMenu'
        cmds.menuItem(divider=True, p=_menu_name)

        _m = cmds.menuItem(_original_menu, subMenu=True, label='AnimMemo Menu', p=_menu_name, to=True)

        cmds.menuItem(label='Create',
                      ann='Create Mew Memo',
                      c=instance.new_memo,
                      p=_m)

        cmds.menuItem(divider=True, p=_original_menu)

        cmds.menuItem(label='DeleteAll',
                      ann='Delete All Memo',
                      c=instance.delete_all_memo,
                      p=_m)

        cmds.menuItem(divider=True, p=_m)

        cmds.menuItem(label='ExportFile',
                      ann='ExportFile',
                      c=instance.export_data,
                      p=_m)

        cmds.menuItem(label='ImportFile',
                      ann='ImportFile',
                      c=instance.import_data,
                      p=_m)

        cmds.menuItem(divider=True, p=_m)

        cmds.menuItem(label='ExportFile(Scnes SameName File)',
                      ann='Export the same name file',
                      c=instance.export_data_samename_file,
                      p=_m)

        cmds.menuItem(label='ImportFile(Scnes SameName File)',
                      ann='Import the same name file',
                      c=instance.import_data_samename_file,
                      p=_m)

        _o = cmds.menuItem(_option_menu, subMenu=True, label='Option', p=_m, to=True)

        self.imp_smf = cmds.menuItem(label='Import SameName File',
                      checkBox=self.get_import_samename_file(),
                      ann='Import the same name file when opening a scene',
                      c=self._change_option,
                      p=_o)

        self.save2scene = cmds.menuItem(label='Save to CurrentScene',
                      checkBox=self.get_save_to_current_scene(),
                      ann='Save to CurrentScene',
                      c=self._change_option,
                      p=_o)

    def _change_option(self, *args):
        cmds.optionVar(iv=[self.OPTVER_IMPORT_SAMENAME_FILE, cmds.menuItem(self.imp_smf, q=True, checkBox=True)])
        cmds.optionVar(iv=[self.OPTVER_SAVE_TO_CURRENT_SCENE, cmds.menuItem(self.save2scene, q=True, checkBox=True)])

    def get_import_samename_file(self):
        _ex = cmds.optionVar(exists=self.OPTVER_IMPORT_SAMENAME_FILE)
        if not _ex:
            return True
        return cmds.optionVar(q=self.OPTVER_IMPORT_SAMENAME_FILE)

    def get_save_to_current_scene(self):
        _ex = cmds.optionVar(exists=self.OPTVER_SAVE_TO_CURRENT_SCENE)
        if not _ex:
            return False
        return cmds.optionVar(q=self.OPTVER_SAVE_TO_CURRENT_SCENE)


#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------
