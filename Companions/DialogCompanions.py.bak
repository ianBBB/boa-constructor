#----------------------------------------------------------------------
# Name:        DialogCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/27/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Companions.DialogCompanions'

import wx

from BaseCompanions import CodeCompanion

class CommonDialogCompanion(CodeCompanion):
    def __init__(self, name, parent):
        CodeCompanion.__init__(self, name)
        self.parent = parent

class DataCDC(CommonDialogCompanion):
    def constructor(self):
        return '    dlg = %(dlgclass)s(%(parent)s, data = None)'

class ColourDialogCDC(DataCDC):
    def body(self):
        return '''data = wx.ColourData()
data.SetChooseFull(True)
dlg = wx.ColourDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetColourData()
        # Your code
finally:
    dlg.Destroy()

'''

class FontDialogCDC(DataCDC):
    def body(self):
        return '''data = wx.FontData()
dlg = wx.FontDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetFontData()
        font = data.GetChosenFont()
        # Your code
finally:
    dlg.Destroy()

'''

class PrintDialogCDC(DataCDC):
    def body(self):
        return '''data = wx.PrintDialogData()
data.EnablePrintToFile(True)
data.EnablePageNumbers(True)
data.EnableSelection(True)
dlg = wx.PrintDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        # Your code
finally:
    dlg.Destroy()

'''

class PageSetupDialogCDC(DataCDC):
    def body(self):
        return '''data = wx.PageSetupDialogData()
data.SetMarginTopLeft(wx.Point(50,50))
data.SetMarginBottomRight(wx.Point(50,50))
dlg = wx.PageSetupDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetPageSetupData()
        # Your code
finally:
    dlg.Destroy()

'''

class MessagedCDC(CommonDialogCompanion):
    pass

class DirDialogCDC(MessagedCDC):
    def body(self):
        return '''dlg = wx.DirDialog(self)
try:
    if dlg.ShowModal() == wx.ID_OK:
        dir = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class FileDialogCDC(MessagedCDC):
    def body(self):
        return '''dlg = wx.FileDialog(self, "Choose a file", ".", "", "*.*", wx.OPEN)
try:
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class SingleChoiceDialogCDC(MessagedCDC):
    def body(self):
        return '''dlg = wx.SingleChoiceDialog(self, 'Question', 'Caption', [])
try:
    if dlg.ShowModal() == wx.ID_OK:
        selected = dlg.GetStringSelection()
        # Your code
finally:
    dlg.Destroy()

'''

class TextEntryDialogCDC(MessagedCDC):
    def body(self):
        return '''dlg = wx.TextEntryDialog(self, 'Question', 'Caption', 'Default answer')
try:
    if dlg.ShowModal() == wx.ID_OK:
        answer = dlg.GetValue()
        # Your code
finally:
    dlg.Destroy()

'''

class MessageDialogCDC(MessagedCDC):
    def body(self):
        return '''dlg = wx.MessageDialog(self, 'Message',
  'Caption', wx.OK | wx.ICON_INFORMATION)
try:
    dlg.ShowModal()
finally:
    dlg.Destroy()

'''

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerComponents('Dialogs',
      (wx.FontDialog, 'wx.FontDialog', FontDialogCDC),
      (wx.FileDialog, 'wx.FileDialog', FileDialogCDC),
      (wx.PrintDialog, 'wx.PrintDialog', PrintDialogCDC),
      (wx.PageSetupDialog, 'wx.PageSetupDialog', PageSetupDialogCDC),
      (wx.DirDialog, 'wx.DirDialog', DirDialogCDC),
      (wx.SingleChoiceDialog, 'wx.SingleChoiceDialog', SingleChoiceDialogCDC),
      (wx.TextEntryDialog, 'wx.TextEntryDialog', TextEntryDialogCDC),
      (wx.MessageDialog, 'wx.MessageDialog', MessageDialogCDC),
    )
