from django.contrib import admin
from Lists_to_RDFs.models import *
from django.forms import TextInput, Textarea
from django.db import models

class RDFInline(admin.TabularInline):
	model = RDF
	extra = 1

class WikiAdmin(admin.ModelAdmin):
	formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        models.TextField: {'widget': Textarea(attrs={'rows':80, 'cols':180})},
    }
	inlines = [RDFInline,]


admin.site.register(WikiList, WikiAdmin)
admin.site.register(RDF)