## Script (Python) "Field"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Field
##
#subfield_default_year, subfield_default_month, subfield_default_day,
#subfield_default_hour, subfield_default_minute

skip_field_types = ['MethodField',]
ctx = context.aq_parent.aq_parent.aq_parent
#fld_prps = {'Messages': ctx.message_values}
fields = [('Messages', ctx.message_values, 'Field.Messages', ())]
field_ids, field_objs = ctx.form.get_field_ids(), ctx.form.get_fields()
for idx in _.range(_.len(field_ids)):
    fld_id = field_ids[idx]
    #m = ctx.get_override(fld_id);if m: m = m.method_name
    tpe = _.str.split(repr(field_objs[idx])[1:])[0]
##        if tpe == 'DateTimeField':
##            fields.append( (fld_id, ctx.values[fld_id], tpe, ()) )
    if tpe not in skip_field_types:
        fields.append( (fld_id, ctx.values[fld_id], tpe, ()) )

return fields
