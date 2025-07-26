import wx
import wx.lib.buttons

def postCommandEvent(ctrl, evtType, evtId = None):
    if evtId is None:
        evtId = ctrl.GetId()
    wx.PostEvent(ctrl, wx.CommandEvent(evtType, evtId))
    wx.Yield()


def test_wxFrame(palette):
    try:
        # New frame
        postCommandEvent(palette.palettePages[0].buttons['wx.Frame'],
                         wx.wxEVT_COMMAND_BUTTON_CLICKED)

        # Open designer
        mp = palette.editor.getActiveModulePage()
        ctrlr = palette.editor.getControllerFromModel(mp.model)
        ctrlr.OnDesigner(None)

        # Select static text
        btn = palette.palettePages[2].buttons['wx.StaticText']
        btn.up = False
        evt = wx.lib.buttons.GenButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, btn.GetId())
        evt.SetButtonObj(btn)
        evt.SetIsDown(True)
        wx.PostEvent(btn, evt)
        wx.Yield()

        # Drop component on Designer
        model = palette.editor.getActiveModulePage().model
        evt = wx.MouseEvent(wx.wxEVT_LEFT_DOWN)
    #        evt.SetEventObject(model.views['Designer'])
        evt.m_x = 10
        evt.m_y = 10
        wx.PostEvent(model.views['Designer'], evt)
        wx.Yield()

        # Select Frame
        evt = wx.MouseEvent(wx.wxEVT_LEFT_DOWN)
        evt.m_x = 0
        evt.m_y = 0
        wx.PostEvent(model.views['Designer'], evt)
        wx.Yield()

        constructorPage = palette.editor.inspector.constr
        for nv in constructorPage.nameValues:
            if nv.propName == 'Name':
                nv.propEditor.inspectorEdit()
                nv.propEditor.editorCtrl.editorCtrl.SetValue('TestFrame')
                nv.propEditor.inspectorPost(False)
                break

        # resize designer
        model.views['Designer'].SetDimensions(10, 10, 200, 200)
        model.views['Designer'].SetPosition( (0, 0) )
        wx.Yield()

        model.views['Designer'].Close()
    except:
        wx.MessageBox('Test failed\n'+`sys.exc_info()`)
    else:
        #if model.data == frame_answer:
        wx.MessageBox('Test succeeded')

frame_answer = '''#Boa:Frame:TestFrame

import wx

def create(parent):
    return TestFrame(parent)

[wxID_TESTFRAME, wxID_TESTFRAMESTATICTEXT1,
] = [wx.NewId() for _init_ctrls in range(2)]

class TestFrame(wx.Frame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_TESTFRAME, name='TestFrame', parent=prnt,
              pos= wx.Point(0, 0), size= wx.Size(200, 200),
              style=wx.DEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wx.Size(192, 173))

        self.staticText1 = wx.StaticText(id=wxID_TESTFRAMESTATICTEXT1,
              label='staticText1', name='staticText1', parent=self,
              pos= wx.Point(0, 0), size= wx.Size(192, 173), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
'''
