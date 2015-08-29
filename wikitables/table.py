import wikitables.sparql as sparql
import itertools
from wikitables.keyExtractor import KeyExtractor
from collections import defaultdict, Counter
from fuzzywuzzy import fuzz
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
        If none is found, use the article's title.
        """
        for sibling in self.soup.previous_siblings:
            if sibling.name in ['h2', 'h3']:
                return sibling.span.text

        for parent in self.soup.parents:
            if parent.has_attr('id') and parent['id'] == 'content':
                return parent.h1.text

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
        """Under the assumption that all columns have equal length.
        """
        return len(self[0])

    def skip(self):
        """The extraction algorithms rely on assumptions about the table's structure.
        In most cases this refers to the absence of cells spanning multiple rows or columns.
        """
        # TODO ? Colspans?
        if not self.rows:
            print(self.page.title)
            print('!!!: not self.rows!?')
            return True

        row_lengths = [len(row) for row in self.rows]  # Skip tables with unequal row lengths
        if max(row_lengths) != min(row_lengths):
            return True

        if max(row_lengths) != len(self.column_names):  # Skip tables with ambiguous headers
            return True

        return False

    def predicates_for_columns(self, sub_column_name, obj_column_name, relative=True):
        """Return all predicates with subColumn's cells as subjects and objColumn's cells as objects.
        Set 'relative' to True if you want relative frequencies.
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

    def predicates_for_all_columns(self, relative=True, omit=False):
        """Return list of ordered column pairs with their relationships and frequencies.
        Use 'omit' to leave out pairs with no relationships present.
        """
        column_pairs = []
        for sub_column, obj_column in itertools.permutations(self.column_names, 2):
            column_pair_predicates = self.predicates_for_columns(sub_column, obj_column, relative)
            if column_pair_predicates or not omit:
                column_pairs.append({
                    'subject': sub_column,
                    'object': obj_column,
                    'predicates': column_pair_predicates
                })
        return column_pairs

    def name_match(self, predicate_identifier, column):
        """Match the identifier of a predicate against the name of the column.
        """
        column_name = (self.column_names[column] if type(column) is int else column)
        predicate_name = predicate_identifier.split('/')[-1:][0]  # remove identifier prefix
        ratio = fuzz.partial_ratio(predicate_name.lower(), column_name.lower())
        return ratio / 100  # Return value from 0 to 1

    def generate_data(self, columns=None):
        """Generate data for all (ordered) pairs of columns.
        See generate_data_for_columns() for further details.
        """
        data = DataFrame(columns=['Subject', 'Predicate', 'Object', 'Frequency',
                                  'isKey', 'nameMatch', 'subjectColumn', 'objectColumn'])

        permutations = itertools.permutations(columns if columns else self.column_names, 2)

        for sub_column_name, obj_column_name in permutations:
            data = data.append(self.generate_data_for_columns(sub_column_name, obj_column_name))

        data['table'] = repr(self)
        data['page'] = self.page.title

        print("Generated %d triples with avg. frequency of %.0f%%." %
              (len(data.index), data['Frequency'].mean() * 100))

        return data

    def generate_data_for_columns(self, sub_column_name, obj_column_name):
        """Generate data for a pair of columns.
        Accumulate predicates already present in SPARQL endpoint and select candidates from this set.
        Apply those candidate predicates to all the rows where they were not already present.
        Return a pandas Table with the resulting triples and
            a) the frequency of the applied predicate
            b) the string proximity of the predicate and the object cell's column name
            c) and whether the subject cell is element of a key column.
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
                'Frequency': value / len(self),  # a)
                'nameMatch': self.name_match(key, obj_column_name)  # b)
            }

        row_candidates = [candidates.keys() - row
                          for row in existing_row_predicates]

        is_key = self.is_key(sub_column_name)  # c)

        # subjectColumn and objectColumn included for later testing
        data = DataFrame(columns=['Subject', 'Predicate', 'Object', 'Frequency',
                                  'isKey', 'nameMatch', 'subjectColumn', 'objectColumn'])
        for i, (sub, obj) in enumerate(cell_pairs):
            if not sparql.is_resource(sub):  # skip subject literals
                continue

            for predicate in row_candidates[i]:
                data.loc[len(data)] = [sub, predicate, obj,
                                       candidates[predicate]['Frequency'],
                                       is_key,
                                       candidates[predicate]['nameMatch'],
                                       sub_column_name,
                                       obj_column_name]

        return data
