from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import WikiList, WikiTable

# Create your views here.
def testKeyExtraction(request):
	page = WikiTable.objects.all()[1]
	html = page.html
	template = loader.get_template('KeyExtractionTest.html')
	context = RequestContext(request, {
		'table': html,
	})
	return HttpResponse(template.render(context))


