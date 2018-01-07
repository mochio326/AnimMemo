# # -*- coding: utf-8 -*-

import maya.cmds as cmds


def __register_animmemo_startup():
    from textwrap import dedent
    cmds.evalDeferred(dedent(
        """
        import animmemo.startup as s
        s.execute()
        """
    ))


if __name__ == '__main__':
    try:
        print("AnimMemo startup script has begun")
        __register_animmemo_startup()
        print("AnimMemo startup script has finished")

    except Exception as e:
        print("AnimMemo startup script has ended with error")
        # avoidng the "call userSetup.py chain" accidentally stop,
        # all exception must be collapsed
        import traceback
        traceback.print_exc()
