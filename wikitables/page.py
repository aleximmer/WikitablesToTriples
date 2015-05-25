import wikipedia
from bs4 import BeautifulSoup
import urllib
from wikitables.table import Table

class TablePage:

    """This class abstracts Wikipedia articles to add table extraction functionality."""

    _html = None
    _soup = None
    _tables = None

    """Use 'contentOnly=True' if you want to filter 'See also' and 'References' sections."""
    def __init__(self, title, contentOnly=True):
        self.page = wikipedia.page(title)
        self.title = self.page.title
        self.url = self.page.url
        self.contentOnly = contentOnly
        if title != self.title:
            print("Loaded \'%s\' instead of \'%s\'" % (self.title, title))

    def __repr__(self):
        return "Title:\n\t%s\nTables:\n\t" % self.title + "\n\t".join([str(t) for t in self.tables])

    @property
    def html(self):
        if not self._html:
            self._html = urllib.request.urlopen(self.url).read()
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

    @staticmethod
    def filteredSections():
        return ['References', 'See also']
