import unittest

from wikitables.table import Table
from testClasses import TestPage

with open ("tests/data/List_of_national_parks_of_the_United_States.html", "r") as html_page:
    text = html_page.read().replace('\n', '')


class TestTableInit(unittest.TestCase):
    def setUp(self):
        self.page = TestPage(text)

    def test_table_init(self):
        tables = self.page.tables
        self.assertEqual(len(tables), 1)


class TestTableMethods(unittest.TestCase):
    def setUp(self):
        self.page = TestPage(text)
        self.table = self.page.tables[0]

    def test_repr(self):
        result = "Table in section 'National Parks'"
        self.assertEqual(result, self.table.__repr__())

    def test_section(self):
        article = 'National Parks'
        self.assertEqual(article, self.table._section())

    def test_key_extraction(self):
        # key is 'name' on first position
        self.assertEqual(0, self.table.key)

    def test_is_key(self):
        self.assertTrue(self.table.is_key(0))
        self.assertTrue(self.table.is_key('Name'))
        self.assertFalse(self.table.is_key(1))
        self.assertFalse(self.table.is_key('Photo'))

    def test_get_item(self):
        self.assertTrue('http://dbpedia.org/resource/Acadia_National_Park' in self.table.__getitem__(0))
        self.assertTrue('http://dbpedia.org/resource/Acadia_National_Park' in self.table.__getitem__('Name'))

    def test_skip(self):
        self.assertFalse(self.table.skip())

    def test_name_match(self):
        values = ['located_in', 'Location']
        match = self.table.name_match(values[0], values[1])
        id_match = self.table.name_match(values[0], 2)
        self.assertEqual(match, id_match)
        self.assertTrue(match <= 1.0 and match >= 0.0)

    def test_str_col_name(self):
        self.assertEqual(self.table._str_column_name(0), self.table._str_column_name('Name'))
