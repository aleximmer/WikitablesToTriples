from wikitables.page import Page
from data.page_data import link_pg, title_pg, summary_pg, categories_pg

class TestPage(Page):
    def __init__(self, html):
        self.url = link_pg
        self._html = html
        self._tables = None
        self._soup = None
        self.title = title_pg
        self._summary = summary_pg
        self._categories = categories_pg

    @property
    def summary(self):
        return self._summary

    @property
    def categories(self):
        return self._categories
