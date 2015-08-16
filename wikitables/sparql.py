from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

wrapper = SPARQLWrapper("http://dbpedia.org/sparql")
wrapper.setReturnFormat(JSON)

# Resource (with redirect) -> Resource (with redirect)
rr_query = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    <%s> dbpedia-owl:wikiPageRedirects* ?subject.
    <%s> dbpedia-owl:wikiPageRedirects* ?object.
    ?subject ?predicate ?object.
}"""

# Resource (with redirect) -> Literal
rl_query = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    <%s> dbpedia-owl:wikiPageRedirects* ?subject.
    ?subject ?predicate ?object.
    FILTER(str(?object)="%s")
}
"""

# Resource (with redirect)
r_query = """
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

select ?subject ?predicate ?object
where {
    <%s> dbpedia-owl:wikiPageRedirects* ?subject.
    ?subject ?predicate ?object.
}
"""

def predicates(sub, obj=None):
    """Return predicates of form '?sub ?predicate ?obj.'"""
    if not is_resource(sub):
        return set()

    if obj:
        query = (rr_query if is_resource(obj) else rl_query) % (sub, obj)
    else:
        query = r_query % sub

    wrapper.setQuery(query)

    try:
        results = wrapper.query().convert()

    except SPARQLExceptions.QueryBadFormed as e:
        print("queryBadFormed-error occured with subject: %s, and object: %s" % (sub, obj))
        return set()

    else:
        return {r['predicate']['value'] for r in results['results']['bindings'] if r}


def cell_content(cell):
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

        return a['href'].replace('/wiki', 'http://dbpedia.org/resource')

def is_resource(str):
    return str.startswith('http://dbpedia.org/resource/')

def predicate_exists(sub, pre, obj):
    return pre in predicates(sub, obj)

def predicate_range(predicate):
    "Return type schema for given predicate."

    query = """
    SELECT ?object
    WHERE {
        <%s> <http://www.w3.org/2000/01/rdf-schema#range> ?object
    }
    """ % predicate

    wrapper.setQuery(query)
    result = wrapper.query().convert()
    return result['results']['bindings'][0]['object']['value']
