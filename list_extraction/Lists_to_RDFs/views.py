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
    table = tables[index]
    htmlTable = table.html

    #----------- 2. generate key for given table
    articleName = str(table.wiki_list.title)
    abstracts = '' #TODO
    tableName = '' #TODO

    try:
        """
        try:
            print(htmlTable[0:500])
            print(articleName)
        except Exception as e:
            print(articleName)
            raise ValueError('Table contains not supported characters - Error message: \n' + str(e))
        """

        # Fix <th> tags because <th> is used in different ways:
        originalHTML = (htmlTable + '.')[:-1] # Save original formatting as copy (force copying)
        htmlTable = fixTableHeaderTagsForOutput(htmlTable)

        # Extracting and rating columns
        uniqueCols = extractUniqueColumns(htmlTable)
        
        # Rating:

        # Zähle die Entities pro Spalte
        countEntities(uniqueCols)

        # Kommt der Artikelname oder das Wort 'Name' im Spaltenname vor
        valuateByName(uniqueCols, articleName)

        # Umso weiter links, umso wertvoller ist die Spalte
        valuateByPosition(uniqueCols)

        # Nutze vertikale TH-Cols
        lookForTHCol(uniqueCols, originalHTML)
        
        # Spaltenname mit der Beschreibung (Abstracts) der Tabelle abgleichen (ähnlich wie mit dem Artikel-Name)
        # TODO: textualEvidenceWithAbstracts(uniqueCols, abstracts)

        # Properties der Spalteneinträge mit den anderen Spaltennamen abgleichen
        # TODO: findFittingColumnProperties(uniqueCols)

        # Listen-Kategorien mit den Spaltennamen abgleichen
        # TODO: findMatchWithListCategories(uniqueCols, articleName)

        # Validiere die Bewertungen der Spalten
        keyCol = validateRatings(uniqueCols)
        
        # Für das Frontend wird die gesamte Anzahl an Spalten benötigt
        colCount = countAllCols(htmlTable)
        
        if keyCol != None:
            keyCol = keyCol['xPos']
        else:
            print('Can\'t extract a significant single key column')
            keyCol = -1

    except Exception as e:
        # Error caused by wrong html format or unsupported html encoding 
        keyCol = -1
        uniqueCols = []
        colCount = countAllCols(htmlTable)

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

