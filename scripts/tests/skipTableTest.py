import wikitables as wt

test_pages = [
    'List of 12th-century BCE lunar eclipses',
    'Apple system on a chip',
    'List of Beetlejuice episodes',
    'List of Björk concert tours',
    'List of boxing septuple champions'
]

for case in test_pages:
    page = wt.Page(case)
    for i, table in enumerate(page.tables):
        print("%s, Table no. %d isSkipped?: %s" % (page.title, i, table.skip()))
