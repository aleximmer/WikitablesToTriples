from django.core.management.base import BaseCommand
from Lists_to_RDFs.models import WikiList, Link
import wikipedia

class Command(BaseCommand):

	def handle(self, *args, **options):
		WikiList.objects.all().delete()
		Link.objects.all().delete()
		counter = 0
		try:
			# Server-Directory containing Titles-File
			listsFile = open('/home/projects/wiki-list_of-retrieval/data/TitlesShuffled.txt', 'r')
			#listsFile = open('/Users/Alex/Documents/workspace/wiki-list_of-retrieval/data/TitlesShuffled.txt', 'r')

		except Exception:
			print('open reading failed')

		for line in listsFile:
			try:
				page = wikipedia.page(line)

				# create new Wiki-List in DB
				newList = WikiList(title=page.title, summary=page.summary, html=page.html(), url=page.url, base_title=line)
				newList.save()

				# Append all links as foreign datasets
				for link in page.links:
					Link(wiki_list=newList, link_name=link).save()

			except Exception:
				continue


			counter = counter + 1
			if counter == 1000:
				return
		return
