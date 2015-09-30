import unittest

from bs4 import BeautifulSoup

from wikitables.page import Page
from testClasses import TestPage


class TestPageInit(unittest.TestCase):
    def test_error(self):
        page_init = lambda: Page()
        self.assertRaises(ValueError, page_init)


class TestPageMethods(unittest.TestCase):
    def setUp(self):
        with open ("tests/data/List_of_national_parks_of_the_United_States.html", "r") as html_page:
            self.text = html_page.read().replace('\n', '')
        self.page = TestPage(self.text)

    def test_repr(self):
        result = self.page.title + ' (' + self.page.url + ')' + "; Tables: Table in section 'National Parks'"
        self.assertEqual(self.page.__repr__(), result)

    def test_html(self):
        self.assertEqual(self.text, self.page.html())

    def test_soup(self):
        self.assertIsInstance(self.page.soup, BeautifulSoup)

    def test_tables(self):
        self.assertEqual(self.page.has_table(), True)
        self.assertEqual(len(self.page.tables), 1)
