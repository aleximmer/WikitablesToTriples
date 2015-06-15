from wikitables.sparql import *

def bestPredicate(page, ignore100=True):
    tables = []

    for table in page['tables']:
        tables += table['predicates']

    predicates = []
    for perm in tables:
        for predicate in perm['predicates']:
            predicates.append(perm['predicates'][predicate])

    if ignore100:
        predicates = [p for p in predicates if not p == 1.0]

    return max(predicates) if len(predicates) > 0 else 0.0

def hasPredicate(sub, obj, predicate):
    return predicate in predicates(sub, obj)
