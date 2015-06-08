# Triples subject is %1 and object is like %2 united with reverse
"""
PREFIX : <http://dbpedia.org/resource/>
select ?subject ?predicate ?object
where {
    {
        ?subject ?predicate ?object.
        FILTER(?subject=:%s)
        FILTER regex(?object, "%s", "i").
    }
    UNION
    {
        ?subject ?predicate ?object.
        FILTER (?object=:%s)
        FILTER regex(?subject, "%s", "i").
    }
}
"""

"""
PREFIX : <http://dbpedia.org/resource/>
PREIFX dbo: <http://dbpedia.org/ontology/>
select ?subject ?predicate ?object
where {
    ?subject dbo:coach :%s.
    FILTER regex(?subject, "%s", "i").
}
""" 
