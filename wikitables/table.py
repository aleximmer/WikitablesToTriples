import wikitables.sparql as sparql
import itertools
from wikitables.keyExtractor import KeyExtractor
from collections import defaultdict, Counter
from fuzzywuzzy import fuzz
from copy import deepcopy
from pandas import DataFrame


class Table:
    """This class abstracts tables in Wikipedia articles to provide additional extraction functionality.
    """

    def __init__(self, soup, page):
        self.soup = soup
        self.caption = soup.find('caption')
        self.head = soup.find('thead')
        self.body = soup.find('tbody')
        self.section = self._section()
        self.column_names = [th.text for th in self.soup.findAll('tr')[0].findAll('th')]
        self.page = page
        self.rows = [[sparql.cell_content(cell) for cell in tr.findAll('th') + tr.findAll('td')] for tr in self.soup.findAll('tr') if tr.find('td')]

    def __repr__(self):
        if self.caption:
            return "\'%s\' in section \'%s\'" % (self.caption.text, self.section)
        return "Table in section \'%s\'" % self.section

    def _section(self):
        """Try finding first header (h2, h3) before table.
        If none found, use the article's title.
        """

        for sibling in self.soup.previous_siblings:
            if sibling.name in ['h2', 'h3']:
                return sibling.span.text

        for parent in self.soup.parents:
            if parent.has_attr('id') and parent['id'] == 'content':
                return parent.h1.text

    def peek(self, chars=400):
        return self.soup.prettify()[:chars]

    def as_dictionary(self, text=False):
        columnDict = {}
        for i, c in enumerate(self.column_names):
            columnDict[c] = [str(row[i]) if text else row[i] for row in self.rows]
        return columnDict

    @property
    def columns(self):
        columns = []
        for i, c in enumerate(self.column_names):
            columns.append([row[i] for row in self.rows])
        return columns

    @property
    def key(self):
        extractor = KeyExtractor(self.soup, self.page.title, self.page.summary, self.page.categories)
        key = extractor.extractKeyColumn()
        if key != None:
            # Key object has following params:
            # entries, unique(no duplicate content), rating, xPos, title
            # entityCount(number of cells with an entity),
            # multipleEntities(true if at least one cell contains 2 entities),
            key = key['xPos']
        return key

    @property
    def key_name(self):
        return self.column_names[self.key]

    def row(self, i):
        return self.rows[i]

    def column(self, key):
        i = key if type(key) is int else self.column_names.index(key)
        return [row[i] for row in self.rows]

    def __getitem__(self, key):
        """Return column by index number or column name.
        """

        i = key if type(key) is int else self.column_names.index(key)
        return [row[i] for row in self.rows]

    def __len__(self):
        """Return number of rows.
        """

        return len(self[0])

    def skip(self):
        # Something's wrong with rows (TODO: find 'something')

        if not self.rows:
            return True

        # Skip tables with unequal row lengths
        if max([len(row) for row in self.rows]) != min([len(row) for row in self.rows]):
            return True

        if max([len(row) for row in self.rows]) != len(self.column_names):
            return True

        return False

    def predicates_for_columns(self, sub_column_name, obj_column_name, relative=True):
        """Return all predicates with subColumn's cells as subjects and objColumn's cells as objects.
        Set 'relative' to True if you want relative occurances.
        """

        predicates = defaultdict(int)
        for sub, obj in zip(self[sub_column_name], self[obj_column_name]):

            if obj and sparql.is_resource(sub):
                for predicate in sparql.predicates(sub, obj):
                    predicates[predicate] += 1

        if relative:
            for p in predicates:
                predicates[p] = round(predicates[p]/len(self[sub_column_name]), 2)

        return dict(predicates)

    def rel_predicates_for_key_column(self, relative=True):
        """Return all predicates with subColumn as subject and all other columns as possible objects.
        Set 'relative' to True if you want relative occurances.
        """

        objPredicates = {}
        for obj in self.column_names:
            if obj == self.key_name:
                continue

            objPredicates[obj] = self.predicates_for_columns(self.key, obj, relative=True)

        return objPredicates

    # def populateRows(self):
    #     TODO
    #     return rows

    def predicates_for_key_column(self):
        # TODO
        """generate a dictionary containing all predicates for each
        entity in the key-column with their predicates.
        """

        subjects = []
        for sub in self.columns[self.key]:
            subjects.append([sub, sparql.predicates(sub)])

        return subjects

    def match_column_for_predicates(self, predicates):
        """return a ratio calculated by matching the given predicates
        names against the column-names of the table.
        """

        ratios = deepcopy(predicates)

        for column in predicates:
            for predicate in predicates[column]:
                matchString = predicate.split('/')[-1:][0]
                ratio = fuzz.ratio(matchString, column)
                ratios[column][predicate] = ratio / 100

        return ratios

    def generate_triples_for_key(self, threshold=0.0, ratings=[0.7, 0.3], out=True):
        """ratings consist of two values (first weighs the relative occurency
        second weighs the string-matching with the column name).
        """

        if not self.key_name or len(ratings) != 2:
            return

        predicates = self.rel_predicates_for_key_column()
        stringRatios = self.match_column_for_predicates(predicates)

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

        subjects = self.predicates_for_key_column()

        triples = []
        index = 0
        for subj in subjects:
            print(subj[0])
            for pred in foundPredicates:
                if foundPredicates[pred] in subj[1] or not self[pred][index]:
                    continue
                triple = [subj[0], foundPredicates[pred], self[pred][index]]
                triples.append(triple)
                if out:
                    print('\tpred: ', end=""), print(triple[1])
                    print('\t\tobj/value: ', end=""), print(triple[2])
            index = index + 1

        return triples

    def generate_triples(self, columns=None, threshold=0.0, path=None):
        """Save RDF statements generated from table.
        """

        data = []
        permutations = itertools.permutations(columns if columns else self.column_names, 2)
        for sub_column_name, obj_column_name in permutations:
            data += self.triples_for_columns(sub_column_name, obj_column_name, threshold=threshold)

        df = DataFrame(data, columns=['subject', 'predicate', 'object', 'certainty'])
        df['table'] = repr(self)
        df['page'] = self.page.title

        print("Generated %d statements with avg. certainty of %.0f%%." % (len(df.index), df['certainty'].mean() * 100))

        if path:
            df.to_csv(path, index=False)

        return df

    def triples_for_columns(self, sub_column_name, obj_column_name, threshold=0.0):
        """Generate triples for a pair of columns.
        Accumulate predicates already present in SPARQL endpoint and select candidates from this set.
        Match the candidates certainty (i.e., how likely they correctly represent the column pair) against the provided threshold.
        Return a Pandas DataFrame for easy saving and printing.
        """

        # Row-wise pairs of cells
        cell_pairs = list(zip(self[sub_column_name], self[obj_column_name]))

        # List of existing predicates for every pair of cells
        existing_row_predicates = [ sparql.predicates(sub, obj) for sub, obj in cell_pairs ]

        # Count occurence of every predicate in every row
        counter = Counter([ predicate
        for row in existing_row_predicates
        for predicate in row ])

        relative_frequencies = dict(
            (key, value/len(self))
            for key, value in counter.items())

        row_candidates = [relative_frequencies.keys() - row for row in existing_row_predicates]

        data = DataFrame(columns=['Subject', 'Predicate', 'Object', 'Frequency', 'isKey', 'nameMatch'])
        for i, (sub, obj) in enumerate(cell_pairs):
            if not sparql.is_resource(sub): # skip subject literals
                continue

            for predicate in row_candidates[i]:
                data.loc[len(data)] = [sub, predicate, obj, relative_frequencies[predicate], False, False]

        return data

    def certainty(self, candidate_predicate, subject_column, object_column, relative_occurence):
        """Calculate a certainty for a given candidate predicate (i.e., how likely it represents the relationship between the column pair).
        """

        # TODO: Subject isKeyColumn?
        # TODO: Predicate matches column name?

        return round(relative_occurence, 2)
        # return {key for key, value in candidate_dict.items() if value > threshold}
