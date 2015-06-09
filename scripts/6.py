import os
import json, csv

testDataPath = './testdata/'
paths = [os.path.join(testDataPath,fn) for fn in next(os.walk(testDataPath))[2] if fn.endswith('.json')]

tables = []
permutations = []
for path in paths:
    with open(path, 'r') as f:
        try:
            page = json.load(f)
        except:
            continue

        tables += page['predicates']
        for table in page['predicates']:
            permutations += [t['predicates'] for t in table['predicates']]

print('Pages: %s' % len(paths))
print('Tables: %s' % len(tables))

with open('./result.json', 'w') as f:
    json.dump(tables, f, indent=4)


for i in range(0, 100):
    value = i/100
    # value = 0.0
    n = len(tables)
    k = 0
    for t in tables:
        predicates = []
        for p in t['predicates']:
            predicates += [p['predicates'][key] for key in p['predicates']]
        if predicates and max(predicates) > value:
            k += 1

    # print('Value: %s, N: %s, k: %s, k/N: %s' % (value, n, k, k/n))
    print('%s, %s' % (value, k/n))
