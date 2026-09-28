"""Demonstrates how to change system constants as a plug-in."""

import sourceconst
# The order of (Name)s may change and lines may also be removed
sourceconst.defInfoBlock = sourceconst.wsfix(
'''#-----------------------------------------------------------------------------
# Name:        %(Name)s
# Purpose:     %(Purpose)s
#
# Author:      %(Author)s
#
# Created:     %(Created)s
# RCS-ID:      %(RCS-ID)s
# Copyright:   %(Copyright)s
# Licence:     %(Licence)s
# New field:   %(NewField)s
#-----------------------------------------------------------------------------
''')

import Preferences
# (Name)s not in the original dictionary needs to be added
Preferences.staticInfoPrefs['NewField'] = 'Whatever'
