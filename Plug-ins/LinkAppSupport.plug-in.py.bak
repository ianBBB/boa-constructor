""" Boa plug-in which allows linking a sub application to a main application.

Add the main application as a file in the modules list.

When run application is performed on the linked application or any of it's
modules, the main application file is run.

Note, as running is always proxied to the main application, you won't be able
to run the link app module itself from the IDE!

Linked apps can be chained but beware of cycles! ;)

Only proxies the run and debug methods to the parent app.

"""

import wx

import Plugins

import sourceconst
from Models import PythonEditorModels, PythonControllers, EditorHelper, Controllers

EditorHelper.imgLinkAppModel = EditorHelper.imgIdxRange()

class LinkAppModel(PythonEditorModels.PyAppModel):
    modelIdentifier = 'LinkApp'
    defaultName = 'LinkApp'
    bitmap = 'LinkApp_s.png'
    imgIdx = EditorHelper.imgLinkAppModel

#    def getDefaultData(self):
#        return sourceconst.defSig %{'modelIdent':self.modelIdentifier, 'main': ''}

    def findAppInModules(self, args):
        for name, Model in self.moduleModels.items():
            if Model.modelIdentifier in Controllers.appModelIdReg:
                filepath = self.moduleFilename(name)
                if self.editor.modules.has_key(filepath):
                    model = self.editor.modules[filepath].model
                else:
                    model = Model('', filepath, '', self.editor, 0, {})
                return model
        return None

    def run(self, args = '', execStart=None, execFinish=None):
        app = self.findAppInModules(args)
        if app:
            app.run(args, execStart, execFinish)
        else:
            wx.LogWarning('No Application module found in modules list to link to')

    def debug(self, params=None, cont_if_running=0, cont_always=0,
              temp_breakpoint=None):
        app = self.findAppInModules(params)
        if app:
            app.debug(params, cont_if_running, cont_always, temp_breakpoint)
        else:
            wx.LogWarning('No Application module found in modules list to link to')
                

class LinkAppController(PythonControllers.BaseAppController):
    Model = LinkAppModel


#-------------------------------------------------------------------------------

Plugins.registerFileType(LinkAppController)
Controllers.appModelIdReg.append(LinkAppModel.modelIdentifier)
