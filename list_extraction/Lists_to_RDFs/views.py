import random
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.http import JsonResponse

from .models import WikiList, WikiTable
from extensions.extractingTables import *
from extensions.table import *

# Create your views here.
"""
Return initial template used for init_testing on Link /KeyForm
"""
def init_testing(request):
    return render(request, 'KeyForm.html')

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

    # table represented by table-module in extensions 
    mod_table = Table(htmlTable)

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

    # get possible ontologies to display for each table
    pos_ontologies = []

    for column in mod_table.columnNames:
        if column != keyCol:
            pos_ontologies.append(mod_table.predicatesForColumns(keyCol, column)

    #----------- 3. Return JsonResponse
    data = {'tableID': table.id, 'tableName': table.title, 'tableHTML': htmlTable, 'keyCol': keyCol, 'colInfos': uniqueCols,
            'colCount': colCount, 'articleName': articleName, 'ontologies': pos_ontologies}
    
    return JsonResponse(data, safe=False)

"""
Store correct key in database but keep algorithm-generated
information in order to optimize the extraction
"""
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
    result = machineLearningWithPrecisionRecall(tables, True) # Print results in console (debug)
	
    return JsonResponse({'precision': result['precision'], 'recall': result['recall'], 'tableCount': result['tableCount'], 'thresholdsState': result['thresholdsState']})




