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
        self.column_names = [th.text for th in self.soup.findAll('tr')[
            0].findAll('th')]
        self.page = page
        self.rows = [[sparql.cell_content(cell) for cell in tr.findAll(
            'th') + tr.findAll('td')] for tr in self.soup.findAll('tr') if tr.find('td')]
        self._key = None

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

    @property
    def key(self):
        if not self._key:
            extractor = KeyExtractor(self)
            self._key = extractor.extractKeyColumn()  # Returns index or -1
        return self._key

    def is_key(self, index):
        return index == self.key if type(index) is int else index == self.column_names[self.key]

    def __getitem__(self, index):
        """Return column by index number or column name.
        """

        i = index if type(index) is int else self.column_names.index(index)
        return [row[i] for row in self.rows]

    def __len__(self):
        return len(self[0])

    def skip(self):
        # TODO: Something is wrong with rows

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
        Set 'relative' to True if you want relative occurrences.
        """

        predicates = defaultdict(int)
        for sub, obj in zip(self[sub_column_name], self[obj_column_name]):

            if obj and sparql.is_resource(sub):
                for predicate in sparql.predicates(sub, obj):
                    predicates[predicate] += 1

        if relative:
            for p in predicates:
                predicates[p] = round(
                    predicates[p] / len(self[sub_column_name]), 2)

        return dict(predicates)

    def rel_predicates_for_key_column(self):
        """Return all predicates with subColumn as subject and all other columns as possible objects.
        Set 'relative' to True if you want relative occurrences.
        """

        obj_predicates = {}
        for obj in self.column_names:

            if obj == self.key:
                continue

            obj_predicates[obj] = self.predicates_for_columns(self.key, obj, relative=True)

        return obj_predicates

    # def populateRows(self):
    #     TODO
    #     return rows

    def predicates_for_key_column(self):
        # TODO
        """generate a dictionary containing all predicates for each
        entity in the key-column with their predicates.
        """

        subjects = []
        for sub in self[self.key]:
            subjects.append([sub, sparql.predicates(sub)])

        return subjects

    def match_column_for_predicates(self, predicates):
        """return a ratio calculated by matching the given predicates
        names against the column-names of the table.
        """

        ratios = deepcopy(predicates)

        for column_name in predicates:
            for predicate in predicates[column_name]:
                ratios[column_name][predicate] = self.name_match(predicate, column_name)

        return ratios

    def name_match(self, predicate, column):
        column_name = (self[column] if type(column) is int else column).lower()
        predicate_name = predicate.split('/')[-1:][0]
        ratio = fuzz.ratio(predicate_name, column_name)
        return ratio / 100

    def generate_triples_for_key(self, threshold=0.0, ratings=[0.7, 0.3], out=True):
        """ratings consist of two values (first weighs the relative frequency
        second weighs the string-matching with the column name).
        """

        if not self.key or len(ratings) != 2:
            return

        predicates = self.rel_predicates_for_key_column()
        string_ratios = self.match_column_for_predicates(predicates)

        # weigh both factors by given ratings
        for column in predicates:
            for predicate in predicates[column]:
                cert = predicates[column][predicate] * ratings[0]
                ratio = string_ratios[column][predicate] * ratings[1]
                predicates[column][predicate] = cert + ratio

        # get highest matching predicate
        found_predicates = {}
        for column in predicates:
            max_val = max(predicates[column], key=lambda p: predicates[column][p])
            if predicates[column][max_val] >= threshold:
                found_predicates[column] = max_val

        subjects = self.predicates_for_key_column()

        triples = []
        index = 0
        for subj in subjects:
            print(subj[0])
            for pred in found_predicates:
                if found_predicates[pred] in subj[1] or not self[pred][index]:
                    continue
                triple = [subj[0], found_predicates[pred], self[pred][index]]
                triples.append(triple)
                if out:
                    print('\tpred: ', end=""), print(triple[1])
                    print('\t\tobj/value: ', end=""), print(triple[2])
            index += 1

        return triples

    def generate_triples(self, columns=None, threshold=0.0, path=None):
        """Save RDF statements generated from table.
        """

        data = []
        permutations = itertools.permutations(
            columns if columns else self.column_names, 2)
        for sub_column_name, obj_column_name in permutations:
            data += self.triples_for_columns(sub_column_name,
                                             obj_column_name, threshold=threshold)

        df = DataFrame(
            data, columns=['subject', 'predicate', 'object', 'certainty'])
        df['table'] = repr(self)
        df['page'] = self.page.title

        print("Generated %d statements with avg. certainty of %.0f%%." %
              (len(df.index), df['certainty'].mean() * 100))

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
        existing_row_predicates = [sparql.predicates(
            sub, obj) for sub, obj in cell_pairs]

        # Count occurrence of every predicate in every row
        counter = Counter([predicate
                           for row in existing_row_predicates
                           for predicate in row])

        candidates = dict()
        for key, value in counter.items():
            candidates[key] = {
                'Frequency': value / len(self),
                'nameMatch': self.name_match(key, obj_column_name)  # Returns the inverse levenshtein distance
            }

        row_candidates = [candidates.keys() - row
                          for row in existing_row_predicates]

        is_key = self.is_key(sub_column_name)

        data = DataFrame(columns=['Subject', 'Predicate', 'Object', 'Frequency', 'isKey', 'nameMatch'])
        for i, (sub, obj) in enumerate(cell_pairs):
            if not sparql.is_resource(sub):  # skip subject literals
                continue

            for predicate in row_candidates[i]:
                data.loc[len(data)] = [sub, predicate, obj,
                                       candidates[predicate]['Frequency'],
                                       is_key,
                                       candidates[predicate]['nameMatch']]

        return data
