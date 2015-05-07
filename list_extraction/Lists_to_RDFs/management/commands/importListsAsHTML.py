from django.core.management.base import BaseCommand
from Lists_to_RDFs.models import WikiList

class Command(BaseCommand):

	def handle(slef, *args, **options):
		# TODO WILLI, put import here:
		print('work on command here')
		# given html contains full html-text and title contains title:
		# WikiList(title=title, html=html).save()
		# creates a WikiList object, id is automated
		return