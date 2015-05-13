 import extractor

print(extractor.extractLists('List of Archdeacons of Eastern Europe', 'ul', lookRecursive=True)[0])
# print(extractor.extractLists('List of South Carolina weather records', 'table', 'wikitable')[0])
# print(str(extractor.extractLists('List of minor planets-61401-61500', 'table', 'wikitable')[0])[0 : 500] + ' [...]')
# print(str(extractor.extractLists('List of Christian denominations by number of members', 'ul')[0])[0 : 500] + ' [...]')