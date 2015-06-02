from bs4 import BeautifulSoup


class Table:

    """This class abstracts tables in Wikipedia articles to provide additional extraction functionality."""

    def __init__(self, soup):
        self.soup = soup
        self.caption = soup.find('caption')
        self.head = soup.find('thead')
        self.body = soup.find('tbody')
        self.section = self._section()

    def __repr__(self):
        if self.caption:
            return self.caption.text
        return "Unnamed table in section \'%s\'" % self.section

    def _section(self):
        """Try finding first header (h2) before table.
        If none found, use the article's title."""
        for sibling in self.soup.previous_siblings:
            if sibling.name == 'h2':
                return sibling.span.text

        for parent in self.soup.parents:
            if parent.has_attr('id') and parent['id'] == 'content':
                return parent.h1.text
