## Script (Python) "SiteErrorLog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=SiteErrorLog
##
"""getProperties is not accesible thru the web."""
# log entry fields: 'tb_text', 'value', 'id', 'type', 'userid', 'url', 'time', 'req_html', 'tb_html', 'username'
return context.aq_parent.aq_parent.getProperties()
