#-----------------------------------------------------------------------------
# Name:        I18NWrap.plug-in.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2006/11/01
# RCS-ID:      $Id$
# Copyright:   (c) 2007
# Licence:     Python
#-----------------------------------------------------------------------------

# msgfmt_* written by Martin v. Lowis from Python/Tools/i18n/msgfmt.py

import os, sys, struct, array

import wx

from Models import EditorModels, Controllers
from ModRunner import ProcessModuleRunner

import Preferences
from Utils import _

Preferences.keyDefs['I18NWrap'] = (wx.ACCEL_ALT, ord('I'), 'Alt-I')

class I18NWrapViewPlugin:
    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.extend( (
         (_('Wrap selection with _()'), self.OnI18NWrapSelection, '-', 'I18NWrap'), 
        ) )

    def OnI18NWrapSelection(self, event):
        first, last = self.view.GetSelection()
        if first and last:
            sel = self.view.GetText()[first:last]
            self.view.ReplaceSelection('_(%s)'%sel)

wxID_POCOMPILE = wx.NewIdRef(count=1)
class POFileController(Controllers.TextController):
    Model = EditorModels.TextModel

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.TextController.actions(self, model) + [
              (_('Compile to MO'), self.OnCompile, '-', '')]

    def OnCompile(self, event):
        model = self.getModel()
        if not model.savedAs:
            wx.LogError(_('Cannot compile an unsaved module'))
            return
        
        filename = model.assertLocalFile()
        outfile = os.path.splitext(filename)[0] + '.mo'
        MESSAGES = {}
        if msgfmt_make(filename, outfile, MESSAGES):
            wx.LogMessage(_('%s created')%outfile)
        else:
            wx.LogError(_('MO file not created'))


def msgfmt_add(id, str, fuzzy, MESSAGES):
    """Add a non-fuzzy translation to the dictionary."""
    if not fuzzy and str:
        MESSAGES[id] = str

def msgfmt_generate(MESSAGES):
    "Return the generated output."
    keys = MESSAGES.keys()
    # the keys are sorted in the .mo file
    keys.sort()
    offsets = []
    ids = strs = ''
    for id in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + '\0'
        strs += MESSAGES[id] + '\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412deL,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size and offset of hash table
    output += array.array("i", offsets).tostring()
    output += ids
    output += strs
    return output


def msgfmt_make(filename, outfile, MESSAGES):
    ID = 1
    STR = 2

    # Compute .mo name from .po name and arguments
    if filename.endswith('.po'):
        infile = filename
    else:
        infile = filename + '.po'

    if outfile is None:
        outfile = os.path.splitext(infile)[0] + '.mo'

    lines = open(infile).readlines()

    section = None
    fuzzy = 0

    # Parse the catalog
    lno = 0
    for l in lines:
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if l[0] == '#' and section == STR:
            msgfmt_add(msgid, msgstr, fuzzy, MESSAGES)
            section = None
            fuzzy = 0
        # Record a fuzzy mark
        if l[:2] == '#,' and l.find('fuzzy'):
            fuzzy = 1
        # Skip comments
        if l[0] == '#':
            continue
        # Now we are in a msgid section, output previous section
        if l.startswith('msgid'):
            if section == STR:
                msgfmt_add(msgid, msgstr, fuzzy, MESSAGES)
            section = ID
            l = l[5:]
            msgid = msgstr = ''
        # Now we are in a msgstr section
        elif l.startswith('msgstr'):
            section = STR
            l = l[6:]
        # Skip empty lines
        l = l.strip()
        if not l:
            continue
        # XXX: Does this always follow Python escape semantics?
        l = eval(l)
        if section == ID:
            msgid += l
        elif section == STR:
            msgstr += l
        else:
            print >> sys.stderr, 'Syntax error on %s:%d' % (infile, lno), \
                  'before:'
            print >> sys.stderr, l
            return
    # Add last entry
    if section == STR:
        msgfmt_add(msgid, msgstr, fuzzy, MESSAGES)

    # Compute output
    output = msgfmt_generate(MESSAGES)

    try:
        open(outfile,"wb").write(output)
    except IOError,msg:
        print >> sys.stderr, msg
        return False
    else:
        return True


Plugins.registerFileType(POFileController, aliasExts=('.po'))
    
from Views import PySourceView
PySourceView.PythonSourceView.plugins += (I18NWrapViewPlugin,)

###-------------------------------------------------------------------------------
##def showGeneratePOTFromSourceDlg(editor):
##    dlg = wx.DirDialog(editor, 
##          _('Select directory to recursively scan source for strings'),
##          _('Generate POT from source'))
##    try:
##        if dlg.ShowModal() == wx.ID_OK:
##            dir = dlg.GetPath()
##            # Your code
##    finally:
##        dlg.Destroy()
##
##Plugins.registerTool(_('Generate POT from source'), showGeneratePOTFromSourceDlg)

