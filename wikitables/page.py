import wikipedia
from bs4 import BeautifulSoup
import requests
from .table import Table

class Page:

    """This class abstracts Wikipedia articles to add table extraction functionality."""

    _html = None
    _soup = None
    _tables = None

    def __init__(self, title, revisionID='', contentOnly=True):
        """Use 'contentOnly=True' if you want to filter 'See also' and 'References' sections."""
        oldID = '&?&oldid='
        if not revisionID:
            oldID = ''
        self.page = wikipedia.page(title)
        self.title = self.page.title
        self.url = self.page.url + oldID + str(revisionID)
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
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup

    @property
    def categories(self):
        return self.page.categories

    @property
    def summary(self):
        return self.page.summary

    @property
    def tables(self):
        if not self._tables:
            self._tables = [Table(table, self) for table in self.soup.findAll('table', 'wikitable')]
        return self._tables

    def hasTable(self):
        return True if self.tables else False

    def predicates(self, relative=True, omit=False):
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

    def browse(self):
        """Open page in browser."""
        import webbrowser

        webbrowser.open(self.url, new=2)
