from bs4 import BeautifulSoup
import sparql as sparql
import itertools
from keyExtractor import extractKeyColumn
import json
from collections import defaultdict
from fuzzywuzzy import fuzz
from copy import deepcopy
from page import *

class Table:

    """This class abstracts tables in Wikipedia articles to provide additional extraction functionality."""

    def __init__(self, soup, page):
        self.soup = soup
        self.caption = soup.find('caption')
        self.head = soup.find('thead')
        self.body = soup.find('tbody')
        self.section = self._section()
        self.columnNames = [th.text for th in self.soup.findAll('tr')[0].findAll('th')]
        self.page = page
        self.rows = [tr.findAll('th') + tr.findAll('td') for tr in self.soup.findAll('tr') if tr.find('td')]

    def __repr__(self):
        if self.caption:
            return "\'%s\' in section \'%s\'" % (self.caption.text, self.section)
        return "Table in section \'%s\'" % self.section

    def _section(self):
        """Try finding first header (h2, h3) before table.
        If none found, use the article's title."""
        for sibling in self.soup.previous_siblings:
            if sibling.name in ['h2', 'h3']:
                return sibling.span.text

        for parent in self.soup.parents:
            if parent.has_attr('id') and parent['id'] == 'content':
                return parent.h1.text

    def peek(self, chars=400):
        return self.soup.prettify()[:chars]

    def asDictionary(self, text=False):
        columnDict = {}
        for i, c in enumerate(self.columnNames):
            columnDict[c] = [str(row[i]) if text else row[i] for row in self.rows]
        return columnDict

    @property
    def columns(self):
        columns = []
        for i, c in enumerate(self.columnNames):
            columns.append([row[i] for row in self.rows])
        return columns

    @property
    def key(self):
        key = extractKeyColumn(self.soup, self.pageTitle, self.pageSummary, self.pageCategories)
        if key != None:
            # Key object has following params:
            # entries, unique(no duplicate content), rating, xPos, title
            # entityCount(number of cells with an entity),
            # multipleEntities(true if at least one cell contains 2 entities),
            key = key['xPos']
        return key

    @property
    def keyName(self):
        return self.columnNames[self.key]

    @property
    def pageTitle(self):
        return self.page.title

    @property
    def pageHTML(self):
        return str(self.soup)

    @property
    def pageSummary(self):
        return self.page.summary

    @property
    def pageCategories(self):
        return self.page.categories

    def row(self, i):
        return self.rows[i]

    def column(self, key, content=False):
        i = key if type(key) is int else self.columnNames.index(key)
        return [sparql.cellContent(row[i]) if content else row[i] for row in self.rows]

    def skip(self):
        # Something's wrong with rows (TODO: find 'something')

        if not self.rows:
            return True

        # Skip tables with unequal row lengths
        if max([len(row) for row in self.rows]) != min([len(row) for row in self.rows]):
            return True

        if max([len(row) for row in self.rows]) != len(self.columnNames):
            return True

        return False

    def predicatesForColumns(self, subColumn, objColumn, relative=True):
        """Return all predicates with subColumn's cells as subjects and objColumn's cells as objects.
        Set 'relative' to True if you want relative occurances."""
        subData = self.column(subColumn)
        objData = self.column(objColumn)
        predicates = {}
        for i in range(0, len(subData)):
            subContent = sparql.cellContent(subData[i])
            objContent = sparql.cellContent(objData[i])

            if not (objContent and sparql.isResource(subContent)):
                continue

            for predicate in sparql.predicates(subContent, objContent):
                if predicate in predicates:
                    predicates[predicate] += 1
                else:
                    predicates[predicate] = 1

        if relative:
            for p in predicates:
                predicates[p] = round(predicates[p]/len(subData), 2)

        return predicates

    def relPredicatesForKeyColumn(self, relative=True):
        """Return all predicates with subColumn as subject and all other columns as possible objects
        Set 'relative' to True if you want relative occurances."""
        objPredicates = {}
        for obj in self.columnNames:
            if obj == self.keyName:
                continue

            objPredicates[obj] = self.predicatesForColumns(self.key, obj, relative=True)

        return objPredicates

    def predicatesForAllColumns(self, relative=True, omit=False):
        """Return predicates between all permutations of columns.
        Set 'omit' to 'True' to leave out empty ones."""
        predicates = []
        for subColumn, objColumn in itertools.permutations(self.columnNames, 2):
            pred = self.predicatesForColumns(subColumn, objColumn, relative)
            if pred or not omit:
                predicates.append({
                    'subject': subColumn,
                    'object': objColumn,
                    'predicates': pred
                })
        return predicates

    # def populateRows(self):
    #     trs = [tr.findAll('td') for tr in self.soup.findAll('tr') if tr.find('td')]
    #     rowLength = len(max(trs, lambda tr: len(tr)))
    #     rows = [[None for cell in range(0, rowLength)] for tr in trs]
    #
    #     for row, tr in enumerate(trs):
    #         col = 0
    #         for td in tr:
    #             while not rows[row][col]: col += 1
    #             rows[row][col] = td
    #
    #     return rows

    def predicatesForKeyColumn(self):
        """generate a dictionary containing all predicates for each
        entity in the key-column with their predicates"""
        subjects = []
        for subject in self.columns[self.key]:
            subjCell = sparql.cellContent(subject)
            subjects.append([subjCell, sparql.predicates(subjCell)])

        return subjects


    def matchColumnForPredicates(self, predicates):
        """return a ratio calculated by matching the given predicates
        names against the column-names of the table"""

        ratios = deepcopy(predicates)

        for column in predicates:
            for predicate in predicates[column]:
                matchString = predicate.split('/')[-1:][0]
                ratio = fuzz.ratio(matchString, column)
                ratios[column][predicate] = ratio / 100

        return ratios


    def generateRDFsForKey(self, threshold=0.0, ratings=[0.7, 0.3], out=True):
        """ratings consist of two values (first weighs the relative occurency
        second weighs the string-matching with the column name)"""

        if not self.keyName or len(ratings) != 2:
            return

        predicates = self.relPredicatesForKeyColumn()
        stringRatios = self.matchColumnForPredicates(predicates)

        # weigh both factors by given ratings
        for column in predicates:
            for predicate in predicates[column]:
                cert = predicates[column][predicate] * ratings[0]
                ratio = stringRatios[column][predicate] * ratings[1]
                predicates[column][predicate] = cert + ratio

        # get highest matching predicate
        foundPredicates = {}
        for column in predicates:
            maxVal = max(predicates[column], key=lambda pred: predicates[column][pred])
            if predicates[column][maxVal] >= threshold:
                foundPredicates[column] = maxVal

        subjects = self.predicatesForKeyColumn()

        triples = []
        index = 0
        for subj in subjects:
            print(subj[0])
            for pred in foundPredicates:
                if foundPredicates[pred] in subj[1] or not self.column(pred, True)[index]:
                    continue
                triple = [subj[0], foundPredicates[pred], self.column(pred, True)[index]]
                triples.append(triple)
                if out:
                    print('\tpred: ', end=""), print(triple[1])
                    print('\t\tobj/value: ', end=""), print(triple[2])
            index = index + 1

        return triples


    def generateRDFs(self, columns=None, threshold=0.0, path=None):
        """Save RDF statements generated from table."""

        data = []

        for subColumnName, objColumnName in itertools.permutations(columns if columns else self.columnNames, 2):
            subColumn = self.column(subColumnName, content=True)
            objColumn = self.column(objColumnName, content=True)

            existingPredicates = [sparql.predicates(subColumn[i], objColumn[i]) for i in range(len(subColumn))]

            absCount = defaultdict(int)
            for row in existingPredicates:
                for predicate in row:
                    absCount[predicate] += 1

            if not absCount:
                continue

            relCount = dict((key, value/len(existingPredicates)) for key, value in absCount.items() if value/len(existingPredicates) > threshold)
            predicates = set(relCount.keys())

            generatedPreciates = [list(predicates - set(row)) for row in existingPredicates]

            for i, row in enumerate(generatedPreciates):
                for predicate in row:
                    data.append([subColumn[i], predicate, objColumn[i], relCount[predicate]])

        # TODO: Bring back after demo
        # from pandas import DataFrame
        # df = DataFrame(data, columns=['subject', 'predicate', 'object', 'certainty'])
        # df['table'] = repr(self)
        # df['page'] = self.pageTitle

        # print("Generated %d statements with avg. certainty of %.0f%%." % (len(df.index), df['certainty'].mean() * 100))

        if path:
            # df.to_csv(path, index=False)
            pass
        else:
            # return df
            # TODO: Remove after demo
            matrix = []
            for row in data:
                matrix.append([row[0], '<' + row[1] + '>', row[2], row[3]])
            s = [[str(e) for e in row] for row in matrix]
            lens = [max(map(len, col)) for col in zip(*s)]
            fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
            table = [fmt.format(*row) for row in s]
            print('\n'.join(table))
            # return df
