## rc-version: 9 ##
# RCS-ID:      $Id$




# Style of the Error/Output window's notebook. GTK is text only
eoErrOutNotebookStyle = 'text'

#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
exCaseInsensitiveSorting = False

#-Editor------------------------------------------------------------------------
# Should there be submenu with all the items from the New palete under the
# Editor's File menu. Causes warnings under wxGTK.
edShowFileNewMenu = False

# Should a custom wxSTC paint handler he installed which minimizes refresing?
edUseCustomSTCPaintEvtHandler = False
# There is a problem with folding on GTK
edSTCFolding = False

#-Window settings---------------------------------------------------------------

# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 210, 'menu': 56}
# Used my Mac toplevel main menu
topMenuHeight = 0

# The amount of space Boa should leave on the right for a vertical OS Taskbar.
verticalTaskbarWidth = 0
# The amount of space Boa should leave from the bottom for a horizontal OS Taskbar.
horizontalTaskbarHeight = 100
# Percentage of the with that the Editor window should occupy
editorScreenWidthPerc = 3.0/4.0

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 16
windowManagerBottom = 7
windowManagerSide = 5

# Font size of the text in the Inspector's statusbar
inspStatBarFontSize = 13

# Match braces in code
braceHighLight = False

# Minimize the IDE while running applications
minimizeOnRun = False

# Minimize the IDE when using Debug/Continue while debugging 
minimizeOnDebug = False

explorerFileSysRootDefault = ('/', '/')

#-Designer----------------------------------------------------------------------

# Draw grid in designer
drawDesignerGrid = False
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = False
# Grid draw method: 'lines', 'dots', 'grid', NYI: 'bitmap'
## options: 'lines', 'dots', 'grid'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = False


# Editable preferences
exportedProperties2 = ['exCaseInsensitiveSorting', 'edShowFileNewMenu',
 'edUseCustomSTCPaintEvtHandler', 'edSTCFolding', 'verticalTaskbarWidth',
 'horizontalTaskbarHeight', 'editorScreenWidthPerc',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'minimizeOnDebug', 'inspStatBarFontSize', 
 'drawDesignerGrid', 'drawDesignerGridForSubWindows',  'drawGridMethod', 
 'grayoutSource',
]
