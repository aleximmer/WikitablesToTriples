from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON
import json

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

def getPredicates(sub, obj):
    query = """
    select ?predicate
    where {
        %s ?predicate %s.
    }
    """ % (sub, obj)
    sparql.setQuery(query)
    results = sparql.query().convert()
    return [r['predicate']['value'] for r in results['results']['bindings']]
