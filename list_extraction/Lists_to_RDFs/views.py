import random
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.http import JsonResponse

from .models import WikiList, WikiTable
from .forms import *

from extensions.extractingTables import *

# Create your views here.
def testKeyExtraction(request):
	page = WikiTable.objects.all()[1]
	html = page.html
	template = loader.get_template('KeyExtractionTest.html')
	context = RequestContext(request, {
		'table': html,
	})
	return HttpResponse(template.render(context))


def get_hum_col(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = TableKeyTest(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # redirect to new random table of tables which haven´t yet been checked
            return HttpResponseRedirect('/KeyForm/')

    # if a GET we append the choices and render an empty template
    else:
        choices = (('test','test'),('none','none'),('another','another'))
        form = TableKeyTest()

    return render(request, 'KeyForm.html', {'form': form})

def init_testing(request):
    # TODO: return thomas´ template here
    return render(request, 'KeyExtractionTest.html')

"""
1. retrieve random Table which is not checked yet
2. generate key for given table
3. return JsonResponse containing tableHTML, key of table and infos about key columna
"""
def get_table_key(request):
    #----------- 1. retrieve random Table
    tables = WikiTable.objects.filter(checked=False)
    upper_border = tables.count() - 1 
    index = random.randint(0, upper_border)
    table = tables[index]
    htmlTable = table.html

    #----------- 2. generate key for given table
    articleName = str(table.wiki_list.title)
    print(articleName)
    print(htmlTable)

    # Extracting and rating columns
    uniqueCols = extractUniqueColumns(htmlTable)
    
    # Rating:

    # Zähle die Entities pro Spalte
    countEntities(uniqueCols)

    # Kommt der Artikelname oder das Wort 'Name' im Spaltenname vor
    valuateByName(uniqueCols, articleName)

    # Umso weiter links, umso wertvoller ist die Spalte
    valuateByPosition(uniqueCols)

    # Validiere die Bewertungen der Spalten
    keyCol = validateRatings(uniqueCols)['xPos']
    print(uniqueCols)
    print(keyCol)

    table.algo_col = str(keyCol)
    #table.save()

    #----------- 3. Return JsonResponse
    data = {'tableID': str(table.id), 'tableHTML': htmlTable, 'keyCol': str(keyCol), 'colInfos': str(uniqueCols)}


    result = json.JSONEncoder().encode(data)
    print(result)

    response = JsonResponse(result, safe=False)
    return response

def get_correct_key(request):
    json_data = json.loads(request.body)
    id = json_data['id']
    key = json_data['key']

    table = WikiTable.objects.get(id=id)
    table.checked = True
    table.hum_col = str(key)
    #table.save()


