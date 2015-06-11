from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
import json

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

# Resource -> Resource
rrQuery = """
select ?predicate
where {
    %s ?predicate %s.
}"""

# Resource -> Literal
rlQuery = """
select ?predicate
where {
    %s ?predicate ?object.
    FILTER(str(?object)="%s")
}
"""

def predicates(sub, obj):
    """Return predicates of form '?sub ?predicate ?obj.'"""

    query = (rrQuery if isResource(obj) else rlQuery) % (sub, obj)
    sparql.setQuery(query)

    try:
        results = sparql.query().convert()

    except SPARQLExceptions.QueryBadFormed as e:
        print("queryBadFormed-error occured with subject: %s, and object: %s" % (sub, obj))
        return []

    else:
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
