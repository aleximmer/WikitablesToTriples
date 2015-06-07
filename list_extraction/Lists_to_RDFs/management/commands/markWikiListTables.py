from django.core.management.base import BaseCommand
from Lists_to_RDFs.models import WikiList, WikiTable
from extensions.page import TablePage

class Command(BaseCommand):

	def handle(self, *args, **options):
		WikiTable.objects.all().delete()

		for page in WikiList.objects.all():
			t_page = TablePage(page.id)
			if t_page.tables:
				page.has_tables = True
			for table in t_page.tables:
				title = table.section
				if not title:
					title = 'None'
				WikiTable(wiki_list=page, title=title, html=table.soup).save()
			page.save()