import wikipedia
from bs4 import BeautifulSoup
import requests
from .table import Table

class Page:

    """This class abstracts Wikipedia articles to add table extraction functionality."""

    _html = None
    _soup = None
    _tables = None

    def __init__(self, title, contentOnly=True):
        """Use 'contentOnly=True' if you want to filter 'See also' and 'References' sections."""
        self.page = wikipedia.page(title)
        self.title = self.page.title
        self.url = self.page.url
        self.contentOnly = contentOnly

    def __repr__(self):
        return "Title:\n\t%s\n\t%s\nTables:\n\t" % (self.title, self.url) + "\n\t".join([str(t) for t in self.tables])

    @property
    def html(self):
        if not self._html:
            self._html = requests.get(self.url).text
        return self._html

    @property
    def soup(self):
        if not self._soup:
            self._soup = BeautifulSoup(self.html)
        return self._soup

    def categories(self):
        return [a.text for a in self.soup.find(id='mw-normal-catlinks').findAll('a')]

    @property
    def tables(self):
        if not self._tables:
            self._tables = [Table(table) for table in self.soup.findAll('table', 'wikitable')]
        return self._tables

    def hasTable(self):
        return True if self.tables else False

    def predicates(self, relative=False, omit=False):
        return {
            'page': self.title,
            'no. of tables': len(self.tables),
            'tables': [
                {
                    'table': repr(table),
                    'colums': table.columnNames,
                    'predicates': table.predicatesForAllColumns(relative, omit)
                } for table in self.tables if not table.skip()]
        }
