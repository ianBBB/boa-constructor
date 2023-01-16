#----------------------------------------------------------------------
# Name:        InspectorEditorControls.py
# Purpose:     Controls that are hosted by the inspector to edit props
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import sys

import wx

import Preferences, Utils

# XXX Refactor all the position offsets into class attribs and move logic
# XXX to the base class

class InspectorEditorControl:
    """ Interface for controls that edit values in the Inspector
        values are stored in the native type of the control       """

    def __init__(self, propEditor, value):
        self.propEditor = propEditor
        self.editorCtrl = None
        self.wID = wx.NewIdRef()
        self.value = value

    def createControl(self):
        if self.editorCtrl: self.editorCtrl.SetFocus()

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            self.editorCtrl.Destroy()
            self.editorCtrl = None

    def getValue(self):
        """ Read value from editor control """
        return self.value

    def setValue(self, value):
        """ Write value to editor control """
        self.value = value

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            height = self.editorCtrl.GetSize().y
            self.editorCtrl.SetSize(wx.Size(width -1, height))

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            self.editorCtrl.SetPosition( (-2, idx*Preferences.oiLineHeight -2) )

    def OnSelect(self, event):
        """ Post the value.

            Bind the event of the control that 'sets' the value to this method
        """
        self.propEditor.inspectorPost(False)
        event.Skip()

class BevelIEC(InspectorEditorControl):
    def destroyControl(self):
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
        InspectorEditorControl.destroyControl(self)

    def createControl(self, parent, idx, sizeX):
        self.bevelTop = wx.Panel(parent, -1,
            (0, idx*Preferences.oiLineHeight -1), (sizeX, 1))
        self.bevelTop.SetBackgroundColour(wx.BLACK)
        self.bevelBottom = wx.Panel(parent, -1,
            (0, (idx + 1)*Preferences.oiLineHeight -1), (sizeX, 1))
        self.bevelBottom.SetBackgroundColour(wx.WHITE)
        
        self.bevelTop.Refresh()
        self.bevelBottom.Refresh()

    def setWidth(self, width):
        if self.bevelTop:
            self.bevelTop.SetSize(wx.Size(width, 1))
            self.bevelBottom.SetSize(wx.Size(width, 1))

    def setIdx(self, idx):
        if self.bevelTop:
            self.bevelTop.SetPosition(wx.Point(-2, idx*Preferences.oiLineHeight -1))
            self.bevelBottom.SetPosition(wx.Point(-2, (idx +1)*Preferences.oiLineHeight -1))

class BeveledLabelIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        BevelIEC.createControl(self, parent, idx, sizeX)
        self.editorCtrl = wx.StaticText(parent, -1, self.value,
            (2, idx*Preferences.oiLineHeight+2),
            (sizeX, Preferences.oiLineHeight-3))
        self.editorCtrl.SetForegroundColour(Preferences.propValueColour)

class TextCtrlIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX, style=wx.TE_PROCESS_ENTER):
        value = self.propEditor.valueToIECValue()
        self.editorCtrl = wx.TextCtrl(parent, self.wID, value,
              (-2, idx*Preferences.oiLineHeight -2),
              (sizeX, Preferences.oiLineHeight+3), style = style)
        parent.Bind(wx.EVT_TEXT_ENTER, self.OnSelect, id=self.wID)
        InspectorEditorControl.createControl(self)

        if value:
            self.editorCtrl.SetSelection(0, len(value))

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.SetValue(value)

class SpinCtrlIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX):
        value = self.propEditor.valueToIECValue()
        self.editorCtrl = wx.SpinCtrl(parent, self.wID, value,
              (-2, idx*Preferences.oiLineHeight -2),
              (sizeX, Preferences.oiLineHeight+3), style=wx.SP_VERTICAL,
              # max=2L**31-1, min=-(2L**31-1))
              max=sys.maxsize, min=-sys.maxsize)
        parent.Bind(wx.EVT_TEXT_ENTER, self.OnSelect, id=self.wID)
        parent.Bind(wx.EVT_SPINCTRL, self.OnSelect, id=self.wID)
        InspectorEditorControl.createControl(self)

        #if value:
        #    self.editorCtrl.SetSelection(0, len(value))

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.GetValue()
        return self.value

    def setValue(self, value):
        self.value = int(value)
        if self.editorCtrl:
            self.editorCtrl.SetValue(self.value)

class ChoiceIEC(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wx.Choice(parent, self.wID,
         wx.Point(-2, idx*Preferences.oiLineHeight -1), 
         wx.Size(sizeX, Preferences.oiLineHeight+3),
         self.propEditor.getValues())
        self.editorCtrl.Bind(wx.EVT_CHOICE, self.OnSelect, id=self.wID)
        InspectorEditorControl.createControl(self)
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetStringSelection()
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetStringSelection(value)
    def repopulate(self):
        self.editorCtrl.Clear()
        for val in self.propEditor.getValues():
            self.editorCtrl.Append(val)


class ComboIEC(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wx.ComboBox(parent, self.wID, self.value,
         wx.Point(-2, idx*Preferences.oiLineHeight -1), wx.Size(sizeX, Preferences.oiLineHeight+3),
         self.propEditor.getValues())
        InspectorEditorControl.createControl(self)
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetStringSelection()
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetSelection(self.editorCtrl.FindString(value))

class ButtonIEC(BevelIEC):
    btnSize = 18
    def createControl(self, parent, idx, sizeX, editMeth):
        bmp = Preferences.IS.load('Images/Shared/ellipsis.png')
        self.editorCtrl = wx.BitmapButton(parent, self.wID, bmp,
          wx.Point(sizeX - self.btnSize - 3, idx*Preferences.oiLineHeight +1),
          wx.Size(self.btnSize, Preferences.oiLineHeight-2))
        self.propValLabel = wx.StaticText(parent, -1, str(self.getValue()),
          wx.Point(2, idx*Preferences.oiLineHeight+2),
          wx.Size(sizeX - self.btnSize - 6, Preferences.oiLineHeight-3),
          style=wx.ST_NO_AUTORESIZE)
        self.editorCtrl.Bind(wx.EVT_BUTTON, editMeth, id=self.wID)
        BevelIEC.createControl(self, parent, idx, sizeX)

    def setWidth(self, width):
        if self.editorCtrl:
            # self.editorCtrl.SetDimensions(width - self.btnSize - 3,
            self.editorCtrl.SetSize(width - self.btnSize - 3,
              self.editorCtrl.GetPosition().y, self.btnSize,
              Preferences.oiLineHeight-2)
            # self.propValLabel.SetDimensions(2,
            self.propValLabel.SetSize(2,
              self.propValLabel.GetPosition().y, width - self.btnSize - 6,
              Preferences.oiLineHeight-3)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetSize(self.editorCtrl.GetPosition().x,
              idx*Preferences.oiLineHeight +2, self.btnSize,
              Preferences.oiLineHeight-2)
            self.propValLabel.SetSize(
              self.propValLabel.GetPosition().x,
              idx*Preferences.oiLineHeight +1, self.propValLabel.GetSize().x,
              Preferences.oiLineHeight-3)

        BevelIEC.setIdx(self, idx)

    def setValue(self, value):
        BevelIEC.setValue(self, value)
        self.propValLabel.SetLabel(str(value))

    def destroyControl(self):
        if self.editorCtrl:
            self.propValLabel.Destroy()
            self.propValLabel = None
        BevelIEC.destroyControl(self)

class TextCtrlButtonIEC(BevelIEC):

    def createControl(self, parent, idx, sizeX, editMeth):
        bmp = Preferences.IS.load('Images/Shared/ellipsis.png')
        value = self.propEditor.valueToIECValue()
        self.wID2 = wx.NewIdRef()
        self.editorCtrl = [
              wx.TextCtrl(parent, self.wID, value,
               (-2, idx*Preferences.oiLineHeight -2),
               (sizeX - 20, Preferences.oiLineHeight+3)),#, style = style),
              wx.BitmapButton(parent, self.wID2, bmp,
               (sizeX - 18 -3, idx*Preferences.oiLineHeight -1),
               (18, Preferences.oiLineHeight))]
        self.editorCtrl[1].Bind(wx.EVT_BUTTON, editMeth, id=self.wID2)
        self.editorCtrl[0].SetFocus()

        if value:
            self.editorCtrl[0].SetSelection(0, len(value))

        BevelIEC.createControl(self, parent, idx, sizeX)
        self.bevelTop.Show(False)
        self.bevelBottom.Show(False)

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            #self.editorCtrl.GetParent().SetFocus()
            for ec in self.editorCtrl:
                ec.Destroy()
            self.editorCtrl = None
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
            self.bevelBottom = None

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            self.editorCtrl[0].SetSize(wx.Size(width -20,
                  self.editorCtrl[0].GetSize().y))
            self.editorCtrl[1].SetDimensions(width - 18 -3,
                  self.editorCtrl[1].GetPosition().y, 18,
                  Preferences.oiLineHeight)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            for ec in self.editorCtrl:
                ec.SetPosition( (ec.GetPosition().x, idx*Preferences.oiLineHeight -2) )
        BevelIEC.setIdx(self, idx)

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl[0].GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl[0].SetValue(value)

class CheckBoxIEC2(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wx.Window(parent, wx.NewIdRef(),
              style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.editorCtrl.SetDimensions(-2, idx*Preferences.oiLineHeight-2,
              sizeX, Preferences.oiLineHeight+3)

        self.checkBox = wx.CheckBox(self.editorCtrl, self.wID, 'False', (2, 1))
        self.editorCtrl.Bind(wx.EVT_CHECKBOX, self.OnSelect, id=self.wID)
        def OnWinSize(evt, win=self.checkBox):
            win.SetSize(evt.GetSize())
        self.editorCtrl.Bind(wx.EVT_SIZE, OnWinSize)

        InspectorEditorControl.createControl(self)

    TrueFalseMap = {True: 'True', False: 'False'}
    def getValue(self):
        if self.editorCtrl:
            return self.TrueFalseMap[self.editorCtrl.GetValue()]
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(self.TrueFalseMap[True] == value)

    def OnSelect(self, event):
        if event.IsChecked():
            self.setValue(self.TrueFalseMap[event.IsChecked()])

        InspectorEditorControl.OnSelect(self, event)

class CheckBoxIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wx.CheckBox(parent, self.wID, 'False',
            (2, idx*Preferences.oiLineHeight+1),
            (sizeX, Preferences.oiLineHeight-2) )
        self.editorCtrl.Bind(wx.EVT_CHECKBOX, self.OnSelect, id=self.wID)

        BevelIEC.createControl(self, parent, idx, sizeX)

    TrueFalseMap = {True: 'True', False: 'False'}
    def getValue(self):
        if self.editorCtrl:
            return self.TrueFalseMap[self.editorCtrl.GetValue()]
        else:
            return self.value
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(
                self.TrueFalseMap[True].lower() == value.lower())

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(2, idx*Preferences.oiLineHeight +1,
            self.editorCtrl.GetSize().x, Preferences.oiLineHeight-2)
        BevelIEC.setIdx(self, idx)
#        InspectorEditorControl.setIdx(self, idx)
    def OnSelect(self, event):
        self.setValue(self.TrueFalseMap[event.IsChecked()])

        BevelIEC.OnSelect(self, event)
