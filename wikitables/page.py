import wikipedia
from bs4 import BeautifulSoup
import requests
from .table import Table

class Page(wikipedia.WikipediaPage):
    'This class abstracts Wikipedia articles to add table extraction functionality.'

    _html = None
    _soup = None
    _tables = None

    def __init__(self, title=None, revisionID='', contentOnly=True, pageid=None, redirect=True, preload=False, original_title='', auto_suggest=True):
        # method taken from wikipedia.page to init OO-Style
        if title is not None:
          if auto_suggest:
            results, suggestion = wikipedia.search(title, results=1, suggestion=True)
            try:
              title = suggestion or results[0]
            except IndexError:
              raise wikipedia.PageError(title)
          super().__init__(title, redirect=redirect, preload=preload)
        elif pageid is not None:
          super().__init__(pageid=pageid, preload=preload)
        else:
          raise ValueError("Either a title or a pageid must be specified")
        #Use 'contentOnly=True' if you want to filter 'See also' and 'References' sections.
        oldID = '&?&oldid='
        if not revisionID:
            oldID = ''
        self.url = self.url + oldID + str(revisionID)
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
