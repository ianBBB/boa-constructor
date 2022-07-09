#----------------------------------------------------------------------
# Name:        Constructors.py
# Purpose:     Definitions mapping property names to constructor
#              keyword arguments
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

class PropertyKeywordConstructor:
    """ The base class for all constructor definitions mapping property
        names to constructor keyword arguments
    """

class EmptyConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {}

class ChoicesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Name': 'name', 'Entries': 'choices'}

class WindowConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style', 'Name': 'name'}
##wxNotebook(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize&
##size, long style = 0, const wxString& name = "notebook")

##wxPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size =
##wxDefaultSize, long style = wxTAB_TRAVERSAL, const wxString& name = "panel")

##wxGrid(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style=0, const
##wxString& name="grid")

## wxStatusBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize&
## size = wxDefaultSize, long style = 0, const wxString& name = "statusBar")

##wxToolBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxTB_HORIZONTAL | wxNO_BORDER, const wxString& name =
##wxPanelNameStr)

##wxScrolledWindow(wxWindow* parent, wxWindowID id = -1, const wxPoint& pos = wxDefaultPosition,
##const wxSize& size = wxDefaultSize long, style = wxHSCROLL | wxVSCROLL, const wxString& name = "scrolledWindow")


class LabeledInputConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Label': 'label',
                'Style': 'style', 'Name': 'name'} 
##wxButton(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos, const wxSize& size
##= wxDefaultSize, long style = 0, const wxValidator& validator, const wxString& name = "button")

##wxCheckBox(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxValidator& val, const
##wxString& name = "checkBox")

##wxRadioButton(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "radioButton")


##class LabeledNonInputConstr(PropertyKeywordConstructor):
##    def constructor(self):
##        return {'Position': 'pos', 'Size': 'size', 'Label': 'label',
##                'Style': 'style', 'Name': 'name'}
##wxStaticBox(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxString& name = "staticBox")

##wxStaticText(wxWindow* parent, wxWindowID id, const wxString& label = "", const wxPoint& pos, const
##wxSize& size = wxDefaultSize, long style = 0, const wxString& name = "staticText")


class ListConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style', 
                'Name': 'name'}
##wxChoice(wxWindow *parent, wxWindowID id, const wxPoint& pos, const wxSize& size, int n, const wxString
##choices[], long style = 0, const wxValidator& validator = wxDefaultValidator, const wxString& name =
##"choice")

##wxListBox(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, int n, const wxString choices[] = NULL, long style = 0, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "listBox")

##wxCheckListBox(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const
##wxSize& size = wxDefaultSize, int n, const wxString choices[] = NULL, long style = 0, const wxValidator&
##validator = wxDefaultValidator, const wxString& name = "listBox")

##wxSpinButton(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxDefaultSize, long style =
##wxSP_HORIZONTAL, const wxValidator& validator = wxDefaultValidator, const wxString& name = "spinButton")

class MultiItemCtrlsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Name': 'name'} 
##wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxLC_ICON, const wxValidator& validator = wxDefaultValidator, const
##wxString& name = "listCtrl")

##wxTreeCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxTR_HAS_BUTTONS, const wxValidator& validator = wxDefaultValidator,
##const wxString& name = "listCtrl")

##wxScrollBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxSB_HORIZONTAL, const wxValidator& validator = wxDefaultValidator,
##const wxString& name = "scrollBar")

