import wx
import wx.xrc

from Utils import _
from PropEdit.PropertyEditors import StrConstrPropEdit

from Companions import BaseCompanions

class XmlResourceDTC(BaseCompanions.UtilityDTC):
    handledConstrParams = ()
    def __init__(self, name, designer, objClass):
        BaseCompanions.UtilityDTC.__init__(self, name, designer, objClass)
        self.editors['FileMask'] = StrConstrPropEdit

##    def hideDesignTime(self):
##        return ['Handle']
    def constructor(self):
        return {'FileMask': 'filemask', 'Name': 'name'}
    def designTimeSource(self, position='wx.DefaultPos', size='wx.DefaultSize'):
        return {'filemask': "''"}
    def writeImports(self):
        return 'import wx.xrc'

    factoryDict = {'LoadPanel'  : 'XrcPanel'}
    def factory(self, method):
        return self.factoryDict.get(method, None)

from Companions import ContainerCompanions
import methodparse

class XrcPanelDTC(ContainerCompanions.PanelDTC):
    suppressWindowId = True
    def constructor(self):
        return {'Name': 'name'}

    def designTimeControl(self, position, size, args = None):
        """ Create and initialise a design-time control """
        if args:
            args['id'] = -1
            self.control = self.ctrlClass(**args)
        else:
            self.control = self.ctrlClass(**self.designTimeDefaults(position, size))

        self.initDesignTimeControl()
        return self.control

    def designTimeDefaults(self, position = wx.DefaultPosition,
                                 size = wx.DefaultSize):
        xrcObjs = self.designer.getObjectsOfClass(wx.xrc.XmlResource)
        if not xrcObjs:
            raise Exception(_('No wx.xrc.XmlResource objects found'))
        # factory/LoadPage allows no positional info
        if not position: posx, posy = 0, 0
        else:            posx, posy = position.x, position.y
        return {'parent': self.parent, 'id': -1, 'pos': (posx, posy),
                'size': (200, 200)}

    xmlResource = ''
    def persistConstr(self, className, params):
        paramStrs = []
        for param in params.keys():
            paramStrs.append('%s = %s'%(param, params[param]))

        if not self.textConstr:
            xrcObjs = self.designer.getObjectsOfClass(wx.xrc.XmlResource)
            names = list(xrcObjs.keys())
            if names:
                dlg = wx.SingleChoiceDialog(self.designer,
                      _('Select wx.xrc.XmlResource to LoadPanel from'),
                      'wx.xrc.XmlResource.LoadPanel', names)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        xrcObj = dlg.GetStringSelection()
                        self.xmlResource = xrcObj.split('.')[1]
                    else:
                        raise Exception('Cancelled!')
                finally:
                    dlg.Destroy()
            else:
                raise Exception(_('No wx.xrc.XmlResource objects found'))
        else:
            self.xmlResource = self.textConstr.factory[0]

        self.textConstr = methodparse.ConstructorParse(
            'self.%s = self.%s.LoadPanel(%s)'%(self.name, self.xmlResource,
            ', '.join(paramStrs)))

        self.designer.addCtrlToObjectCollection(self.textConstr)

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'name': repr(self.name)}


class XrcPanel(wx.Panel):
    pass

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerComponent('Utilities (Data)', wx.xrc.XmlResource,
                          'wx.xrc.XmlResource', XmlResourceDTC)
Plugins.registerComponent('ContainersLayout', XrcPanel,
                          'XrcPanel', XrcPanelDTC)
