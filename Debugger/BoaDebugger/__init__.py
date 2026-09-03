#-----------------------------------------------------------------------------
# Name:        __init__.py
# Purpose:
#
# Author:      gogo@bluedynamics.com, phil@bluedynamics.com
#              robert@bluedynamics.com
# Created:     2003/10/04
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------

# pyright: ignore
# type: ignore

import BoaDebugger, zLOG
from AccessControl import ModuleSecurityInfo
from AccessControl.Permissions import view_management_screens

ModuleSecurityInfo('sys').declarePublic('breakpoint')

__doc__ = 'BoaDebugger'
__version__ = 'Version 0.1'


def initialize(context):
    """
    Add the BoaDebugger to the Zope root
    """
    #
    # need this for icon registration :)
    #
    context.registerClass(
        BoaDebugger.BoaDebugger,
        permission=view_management_screens,
        visibility = None,
        constructors=(BoaDebugger.manage_addBoaDebugger,),
        icon='www/boa.gif',
    )
    context.registerHelp()

    app = context._ProductContext__app
    if not hasattr(app, 'BoaDebugger'):
        try:
            BoaDebugger.manage_addBoaDebugger(app)
            get_transaction().note('Added BoaDebugger')
            get_transaction().commit()
            zLOG.LOG('BoaDebugger', zLOG.INFO, 'Created new BoaDebugger')
        except:
            zLOG.LOG('BoaDebugger', zLOG.ERROR, 'Failed to create new BoaDebugger!')
            raise
