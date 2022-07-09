#----------------------------------------------------------------------
# Name:        ImageStore.py
# Purpose:     Centralised loading of images, supports different 
#              methods of loading: image files, zip files and modules
#
# Author:      Riaan Booysen
#
# Created:     2000/03/15
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     BSD
#----------------------------------------------------------------------

import sys, os, cStringIO

import wx
_ = wx.GetTranslation

class ImageStoreError(Exception): pass
class InvalidImgPathError(ImageStoreError): pass
class UnhandledExtError(ImageStoreError): pass

class ImageStore:

    Error = ImageStoreError
    
    def __init__(self, rootpaths, images=None, cache=1):
        if not images: images = {}
        self.rootpaths = []
        self.images = images
        self.useCache = cache
        
        self.dataReg = {}

        for rootpath in rootpaths:
            self.addRootPath(rootpath)

    def cleanup(self):
        self.images = {}
        self.dataReg = {}

    def createImage(self, filename, ext):
        if ext == '.bmp':
            return wx.Image(filename, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        elif ext == '.png':
            return wx.Image(filename, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        elif ext == '.jpg':
            return wx.Image(filename, wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        elif ext == '.gif':
            return wx.Image(filename, wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        elif ext == '.ico':
            return wx.Icon(filename, wx.BITMAP_TYPE_ICO)
        elif ext == 'data':
            stream = cStringIO.StringIO(self.dataReg[filename])
            bitmap = wx.BitmapFromImage(wx.ImageFromStream(stream))
            if filename[-3:].lower() == 'ico':
                icon = wx.EmptyIcon()
                icon.CopyFromBitmap(bitmap)
                return icon
            else:
                return bitmap
        else:
            raise UnhandledExtError, _('Extension not handled: %s')%ext

    def pathExtFromName(self, root, name):
        imgPath = self.canonizePath(os.path.join(root, name))
        ext = os.path.splitext(name)[1]
        self.checkPath(imgPath)
        return imgPath, ext

    def load(self, name):
        if name in self.dataReg:
            return self.createImage(name, 'data')
            
        for rootpath in self.rootpaths:
            try:
                imgpath, ext = self.pathExtFromName(rootpath, name)
            except InvalidImgPathError:
                continue

            if self.useCache:
                if not self.images.has_key(name):
                    self.images[name] = self.createImage(imgpath, ext)
                return self.images[name]
            else:
                return self.createImage(imgpath, ext)
        raise InvalidImgPathError, _('%s not found in image paths')%name

    def canonizePath(self, imgPath):
        return os.path.normpath(imgPath).replace('\\', '/')

    def checkPath(self, imgPath):
        if imgPath in self.dataReg:
            return

        if not os.path.isfile(imgPath):
            raise InvalidImgPathError, _('%s not valid') %imgPath

    def addRootPath(self, rootPath):
        self.rootpaths.append(rootPath)

    def registerImage(self, name, data):
        self.dataReg[name] = data

class ZippedImageStore(ImageStore):
    def __init__(self, rootpaths, images=None, cache=1):
        self.archives = {}
        ImageStore.__init__(self, rootpaths, images, cache)

    def addRootPath(self, rootPath):
        ImageStore.addRootPath(self, rootPath)

        archive = os.path.join(rootPath, 'Images.archive.zip')
        if os.path.exists(archive):
            print 'reading image archive...'
            import zipfile
            zf = zipfile.ZipFile(archive)
            self.archives[archive] = [fl.filename for fl in zf.filelist]

            for imgPath in self.archives[archive]:
                if imgPath[-1] == '/':
                    continue

                imgData = zf.read(imgPath)
                self.registerImage(imgPath, imgData)

            zf.close()
        else:
            print 'image archive %s not found'%archive

    def load(self, name):
        name = self.canonizePath(name)
        
        if name in self.dataReg:
            return self.createImage(name, 'data')
        else:
            return ImageStore.load(self, name)


class ResourceImageStore(ImageStore):
    def __init__(self, rootpaths, images=None, cache=1):
        ImageStore.__init__(self, rootpaths, images, cache)

    def subModuleImport(self, name):     
        realSysPath = sys.path
        try:
            for path in self.rootpaths:
                sys.path = [path]
                try:
                    mod = __import__(name) 
                except ImportError:
                    continue
                
                components = name.split('.') 
                for comp in components[1:]: 
                    mod = getattr(mod, comp) 
                return mod 
            raise ImportError, _('Could not find %s')%name
        finally:
            sys.path = realSysPath

    def load(self, pathName):
        name = self.transformPathToModuleSpace(pathName)
        if name not in self.dataReg:
            try:
                mod = self.subModuleImport(name)
            except ImportError, err:
                #print '%s not found: %s'%(name, str(err))
                return ImageStore.load(self, pathName)
            self.dataReg[name] = mod.data

        return ImageStore.load(self, name)

    def registerImage(self, name, data):
        name = self.transformPathToModuleSpace(name)
        ImageStore.registerImage(self, name, data)
        
    def transformPathToModuleSpace(self, name):
        name = self.canonizePath(name)
        name = name.replace('.', '_').replace('/', '.')
        return name

        
ImageStoreClasses = {
     'files': ImageStore,
     'zip' : ZippedImageStore,
     'resource': ResourceImageStore,
}     
