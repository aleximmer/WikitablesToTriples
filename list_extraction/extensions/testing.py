from page import Page

pg = Page('List of national parks of India')
tb = pg.tables[0]
print(pg.tables[0])
print(tb.key)
#print(tb.predicatesForColumns('Name', 'State'))
