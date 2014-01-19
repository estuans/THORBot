"""
GUI Handler
"""

import wx


def apwindow():

    apw = wx.App(False)
    fr = wx.Frame(None, wx.ID_ANY, "THORBot Interface")
    fr.Show(True)
    apw.MainLoop()