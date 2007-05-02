from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core import serializers

from django import newforms as forms
from django.newforms import widgets

xmltemplate = """<?xml version="1.0" encoding="UTF-8"?>
<response success="%s">
%s
</response>
"""

class ContactForm(forms.Form):
    firstname = forms.CharField(max_length=20, required=True)
    lastname  = forms.CharField(max_length=20, required=True)
    company   = forms.CharField(initial="default inc.", max_length=20, required=True)
    email     = forms.EmailField(required=True)
    date      = forms.DateField(required=True)
    enable    = forms.BooleanField(required=False)
    
    def clean_firstname(self):
	""" newform extra validator for firstname """
	if len(self.clean_data['firstname'])<10:
	    raise forms.ValidationError("Firstname must be larger then 10 chars.<br/><i>Yeah i know that's a long first name :) but it's good to test out server side validation ;-)</i>");
	return self.clean_data['firstname']

    def clean_email(self):
	""" newform extra validator for email """
	if not self.clean_data['email'].endswith("extjs.com"):
	    raise forms.ValidationError("Email domain must be extjs.com.<br/><i>Another serverside validation example, make sure the email address is in the form of my_name@extjs.com</i>");
	return self.clean_data['email']

    def ext_company(self):
	""" ExtJS extra client side textfield/vtype validator for company """
	config = {
	    'vtype': 'inc', # vtype name, below is dynamic vtype definition
	    'vtypeText': "Must end with 'inc.' <br/><i>This is a vtypes inserted from the django (serverside) it is not part of the standard ExtJS Vtypes set.</i>",
	    'vtypeFunc': """function(v) {
		return /^.*(inc.?)$/i.test(v);
	    }"""
	}
	return config

    def as_extml(self):
	#formmap = dict((key, value.__str__()[24:].split(" ", 1)[0]) for key, value in f.base_fields.items())
	from django.newforms.fields import *
	django_ext_map = {
    	    CharField: ["Ext.form.TextField", {}],
	    IntegerField: ["Ext.form.NumberField", {}],
	    DateField: ["Ext.form.DateField", {}],
	    EmailField: ["Ext.form.TextField", {'vtype':'email'}],
	    URLField: ["Ext.form.TextField", {'vtype':'url'}],
	    BooleanField: ["Ext.form.Checkbox", {}],
	}
	xml = ""
	for name, field in self.fields.items():
	    type, config = django_ext_map[field.__class__]
	    ## Since field type match it doesnt check field for which options is may carry
	    ## TODO: improve this into a more general structure
	    # textfield
	    if hasattr(field, 'required') and field.required:
		config['allowBlank'] = field.required and "false" or "true"
	    if hasattr(field, 'max_length') and field.max_length:
		config['maxLength'] = field.max_length
	    if hasattr(field, 'initial') and field.initial:
		config['value'] = field.initial
	    # numberfield
	    if hasattr(field, 'max_value') and field.max_value:
		config['maxValue'] = field.max_value
	    if hasattr(field, 'min_value') and field.min_value:
		config['minValue'] = field.min_value
	    # general
	    if hasattr(field, 'label') and field.label:
		config['fieldLabel'] = field.label
	    else:
		config['fieldLabel'] = name
	    ## EXT Parameters with no django equiv
	    ##   config['blankText'] = 
	    ## DJANGO Parameters with no ext equiv
	    ##   config['help_text'] = 
	    
	    # apply extra ext validators
	    if hasattr(self, 'ext_'+name):
		config.update(getattr(self, 'ext_'+name)())
	    
	    xml += """<field>
	        <id>%s</id>
    	        <type>%s</type>
		<config><![CDATA[%s]]></config>
	    </field>""" % (name, type, config)
	return "<form>"+xml+"</form>"

def index(request):
    t = loader.get_template("extdjango/index.html")
    f = ContactForm()
    c = Context({
	'form': f.as_table(),
    })
    return HttpResponse(t.render(c))

def extform(request):
    #if not request.POST:
    #	raise Http404
    f = ContactForm()
    #formmap = dict((key, value.__str__()[24:].split(" ", 1)[0]) for key, value in f.base_fields.items())
    #return HttpResponse("%r" % formmap, mimetype="application/json") #json
    xml = f.as_extml()
    xml = xmltemplate % ("true", xml)
    return HttpResponse(xml, mimetype="text/xml")

def extformsubmit(request):
    valid = "false"
    xml = ""
    if request.POST and request.POST.has_key("submit"):
	f = ContactForm()
	valid_keys = f.base_fields.keys()
	valid_data = dict((key, value) for key, value in request.POST.items() if key in valid_keys)
	f = ContactForm(valid_data)
	valid = f.is_valid() and "true" or "false"
	if not f.is_valid():
	    xml+="<errors>"
	    for key, value in f.errors.items():
	    	xml+="""<field>
		    <id>%s</id>
	    	    <msg><![CDATA[%s]]></msg>
		</field>""" % (key, value)
	    xml+="</errors>"
    else:
	xml+="<error>invalid request</error>"
    xml = xmltemplate % (valid, xml)
    return HttpResponse(xml, mimetype="text/xml")

