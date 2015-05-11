from django.core.management.base import BaseCommand
from Lists_to_RDFs.models import WikiList, Link
import wikipedia

class Command(BaseCommand):

	def handle(slef, *args, **options):
		# Server-Directory containing Titles-File
		try:
			listsFile = open('/home/projects/wiki-list_of-retrieval/data/Titles.txt', 'r')

		except Exception:
			print('open reading failed')

		failures = 0

		for line in listsFile:

			try:
				page = wikipedia.page(line.decode('unicode-escape'))

				# create new WIki-List in DB
				newList = WikiList(title=page.title, summary=page.summary, html=page.html(), url=page.url).save()

				# Append all links as foreign datasets
				for link in page.links:
					newLink = Link(wiki_list = newList, linkName=link).save()


			except Exception:
				print("Failure, but continue")
        		failures = failures + 1
        		continue

		print(failures)

		return
