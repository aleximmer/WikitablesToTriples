from django.contrib import admin
from Lists_to_RDFs.models import *
from django.forms import TextInput, Textarea
from django.db import models

class RDFInline(admin.TabularInline):
	model = RDF
	extra = 1

class LinkInline(admin.TabularInline):
	model = Link
	extra = 1
	formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'160'})},
    }

class WikiTableInline(admin.TabularInline):
	model = WikiTable
	extra = 0
	formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':90})},
    }

class WikiAdmin(admin.ModelAdmin):
	formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        models.TextField: {'widget': Textarea(attrs={'rows':30, 'cols':180})},
    }
	inlines = [LinkInline, RDFInline, WikiTableInline]
	list_display = ['title', 'url_ref']
	list_display_links = ['title',]



admin.site.register(WikiList, WikiAdmin)
admin.site.register(WikiTable)
#admin.site.register(RDF)
#admin.site.register(Link)