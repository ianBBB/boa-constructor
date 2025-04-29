import os, sys

import Preferences, Utils, Plugins

if not Plugins.transportInstalled('ZopeLib.ZopeExplorer'):
    # raise Plugins.SkipPlugin, 'Zope support is not enabled'  orig
    raise Exception('Zope support is not enabled', Plugins.SkipPlugin)

#---Model-----------------------------------------------------------------------

# Define new zope image and a Model for opening in the Editor
from ZopeLib.ZopeEditorModels import addZOAImage, ZOAIcons, ZopeDocumentModel, ZopeController
import Models
from Models import Controllers, EditorHelper
from Models.HTMLSupport import HTMLFileModel, HTMLFileController, HTMLFileView

addZOAImage('Page Template', 'Images/ZOA/ZopePageTemplate.png')
addZOAImage('Filesystem Page Template', 'Images/ZOA/ZopePageTemplate.png')

class ZopePageTemplateModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['Page Template']

EditorHelper.imgZopePTFSModel = EditorHelper.imgIdxRange()

class ZopePageTemplateFSModel(HTMLFileModel):
    modelIdentifier = 'PageTemplateHTML'
    defaultName = 'pagetemplate'
    bitmap = 'ZopePageTemplate_s.png'
    imgIdx = EditorHelper.imgZopePTFSModel
    ext = '.pt'

EditorHelper.modelReg[ZopePageTemplateFSModel.modelIdentifier] = ZopePageTemplateFSModel
EditorHelper.extMap['.pt'] = ZopePageTemplateFSModel
EditorHelper.extMap['.zpt'] = ZopePageTemplateFSModel

#---Views-----------------------------------------------------------------------

from ZopeLib import ZopeViews

ZopeViews.zope_additional_attributes += \
      'tal tal:block tal:content tal:replace tal:condition tal:attributes '\
      'tal:define tal:repeat tal:omit-tag tal:on-error '\
      'tales '\
      'metal metal:block metal:use-macro metal:define-macro metal:fill-slot '\
      'metal:define-slot '\
      'i18n i18n:translate i18n:attributes '

class ZopePTHTMLView(ZopeViews.ZopeHTMLView):
    viewName = 'Source.html'
    viewTitle = 'Source.html'
    def generatePage(self):
        props = self.model.transport.properties
        url = 'http://%s:%s@%s:%d/%s/source.html'%(props['username'],
              props['passwd'], props['host'], props['httpport'],
              self.model.transport.whole_name())
        import urllib
        f = urllib.urlopen(url)
        return f.read()

#---Controller------------------------------------------------------------------
class PageTemplateZopeController(ZopeController):
    def OnSave(self, event):
        ZopeController.OnSave(self, event)
        # trigger a reload after saving so that errors saved as comments in the
        # source are displayed
        self.OnReload(event)

class PageTemplateFSController(HTMLFileController):
    Model           = ZopePageTemplateFSModel
    DefaultViews    = [ZopeViews.ZopeHTMLSourceView]
    AdditionalViews = [HTMLFileView]

# Connect controller to the model
Controllers.modelControllerReg[ZopePageTemplateModel] = PageTemplateZopeController
Controllers.modelControllerReg[ZopePageTemplateFSModel] = PageTemplateFSController

#---Explorer--------------------------------------------------------------------

# Node in the explorer
from ZopeLib.ZopeExplorer import ZopeNode, zopeClassMap
class PageTemplateNode(ZopeNode):
    Model = ZopePageTemplateModel
    defaultViews = (ZopeViews.ZopeDebugHTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView, ZopeViews.ZopeSecurityView,
                       ZopePTHTMLView, ZopeViews.ZopeHTMLView)
    def save(self, filename, data, mode='wb'):
        self.getResource().pt_upload('', data)

zopeClassMap['Page Template'] = PageTemplateNode

#---Companion-------------------------------------------------------------------

# Companion used for creation from palette and inspection/posting of props
from ZopeLib.ZopeCompanions import CustomZopePropsMixIn, ZopeCompanion
class PageTemplateZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/PageTemplates/'
        mime, res = self.call(self.objPath, prodPath+'manage_addPageTemplate',
              id = self.name, title = '')

    def getProps(self):
        path, name = os.path.split(self.objPath)
        mime, res = self.call(path, 'zoa/props/PageTemplate', name=name)
        return eval(res)

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value
        path, name = os.path.split(self.objPath)

        mime, res = self.call(self.objPath, 'pt_editAction',
            title = props['title'],
            text = self.call(self.objPath, 'document_src'),
            content_type = props['content_type'],
            expand = props['expand'])

    propOrder = ('title', 'content_type', 'expand')
    propTypeMap = {'title':       ('string', 'title'),
                   'content_type':('string', 'content_type'),
                   'expand':      ('boolean', 'expand'),
                  }

# Add to the Zope palette
import PaletteStore
PaletteStore.paletteLists['Zope'].append('Page Template')
PaletteStore.compInfo['Page Template'] = ['ZopePageTemplate', PageTemplateZC]
