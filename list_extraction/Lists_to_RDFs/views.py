import random
import json
import sys
import io
import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.http import JsonResponse

from .models import WikiList, WikiTable
from .forms import *

from extensions.extractingTables import *

# TODO: Bugfix "\u2014 maps to undefined" but console output is delayed
"""
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'xmlcharrefreplace')
print('Hi: ' + sys.stdout.errors)
"""
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
    # Example for colspan="1" -> Allow
    """
    for i in range(0, len(tables)):
        if tables[i].id == 1212:    
            index = i
    """
    table = tables[index]
    htmlTable = table.html

    #----------- 2. generate key for given table
    articleName = str(table.wiki_list.title)
    abstracts = '' #TODO
    tableName = '' #TODO

    # See extensions/extractingTables.py for algorithm informations
    result = extractKeyColumn(htmlTable, articleName, tableName, abstracts)
    htmlTable = result['originalHTML']
    uniqueCols = result['uniqueCols']
    colCount = result['colCount']
    keyCol = result['keyCol']

    table.algo_col = str(keyCol)
    table.save()

    #----------- 3. Return JsonResponse
    data = {'tableID': table.id, 'tableName': table.title, 'tableHTML': htmlTable, 'keyCol': keyCol, 'colInfos': uniqueCols,
            'colCount': colCount, 'articleName': articleName}
    response = JsonResponse(data, safe=False)
    return response

def get_correct_key(request):
    id = request.GET['id']
    key = request.GET['key']

    table = WikiTable.objects.get(id=id)
    table.checked = True
    table.hum_col = str(key)
    table.save()
    return JsonResponse(['Thanks'], safe=False)

def get_prec_rec(request):
    # Retrieve all rated tables
    tables = WikiTable.objects.filter(checked=True)
    result = testWithCustomThresholds(tables, True) # Print results in console (debug)
	# TODO: Machine learning for thresholdStates
	
    return JsonResponse({'precision': result['precision'], 'recall': result['recall'], 'tableCount': result['tableCount'], 'thresholdsState': result['thresholdsState']})




