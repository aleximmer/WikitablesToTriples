from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
import json

wrapper = SPARQLWrapper("http://dbpedia.org/sparql")
wrapper.setReturnFormat(JSON)

# Resource (with redirect) -> Resource (with redirect)
rrQuery = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    %s dbpedia-owl:wikiPageRedirects* ?subject.
    %s dbpedia-owl:wikiPageRedirects* ?object.
    ?subject ?predicate ?object.
}"""

# Resource (with redirect) -> Literal
rlQuery = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    %s dbpedia-owl:wikiPageRedirects* ?subject.
    ?subject ?predicate ?object.
    FILTER(str(?object)="%s")
}
"""

# Resource (with redirect)
rQuery = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    %s dbpedia-owl:wikiPageRedirects* ?subject.
    ?subject ?predicate ?object.
}
"""

def predicates(sub, obj=None):
    """Return predicates of form '?sub ?predicate ?obj.'"""
    if not isResource(sub):
        return []

    if obj:
        query = (rrQuery if isResource(obj) else rlQuery) % (sub, obj)
    else:
        query = rQuery % sub
    wrapper.setQuery(query)

    try:
        results = wrapper.query().convert()

    except SPARQLExceptions.QueryBadFormed as e:
        print("queryBadFormed-error occured with subject: %s, and object: %s" % (sub, obj))
        return []

    else:
        # print(list(set([r['predicate']['value'] for r in results['results']['bindings'] if r])))
        return list(set([r['predicate']['value'] for r in results['results']['bindings'] if r]))


def cellContent(cell):
    """Return cell's content ready to be used in SPARQL requests."""

    #Remove references
    for sup in cell.findAll('sup'):
        sup.decompose()

    #Remove breaks
    for br in cell.findAll('br'):
        br.decompose()

    #Try find a
    a = cell.find('a', href = True)
    if not a:
        literal = cell.text.strip('\n \"')
        literal = ' '.join(literal.split())
        literal = literal.replace('\\', '\\\\')
        literal = literal.replace('"', '\\"')
        return literal
    else:
        #Handle red links
        if a.has_attr('class') and 'new' in a['class']:
            return a.text

        return a['href'].replace('/wiki', '<http://dbpedia.org/resource') + '>'

def isResource(str):
    return str.startswith('<http://dbpedia.org/resource/')

def predicateExists(sub, pre, obj):
    return pre in predicates(sub, obj)
