from Preferences import IS
from Utils import _


paletteLists = {'New': [],
                'Dialogs': [],
                'Zope': [],
}

newPalette = [_('New'), 'Editor/Tabs/New', paletteLists['New']]
palette = []
dialogPalette =  [_('Dialogs'), 'Editor/Tabs/Dialogs', paletteLists['Dialogs']]
zopePalette =  [_('Zope'), 'Editor/Tabs/Zope', paletteLists['Zope']]

helperClasses = {}
compInfo = {}
newControllers = {}

artProviderArtIds = []

#-------------------------------------------------------------------------------

def loadBitmap(name):
    """ Loads bitmap if it exists, else loads default bitmap """
    imgPath = 'Images/Palette/' + name+'.png'
    try:
        return IS.load(imgPath)
    except IS.Error:
        return IS.load('Images/Palette/Component.png')


def bitmapForComponent(wxClass, wxBase='None'):
    """ Returns a bitmap for given component class.

    "Aquires" bitmap by traversing inheritance thru if necessary.
    """
    if wxBase != 'None': return loadBitmap(wxBase)
    else:
        cls = wxClass
        try: bse = wxClass.__bases__[0]
        except:
            # if compInfo.has_key(wxClass):
            if wxClass in compInfo:
                return loadBitmap(compInfo[wxClass][0])
            else:
                return loadBitmap('Component')
        try:
            # while not compInfo.has_key(cls):
            while cls not in compInfo:
                cls = bse
                bse = cls.__bases__[0]

            return loadBitmap(compInfo[cls][0])
        except:
            return loadBitmap('Component')
