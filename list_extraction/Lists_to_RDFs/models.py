from django.db import models

class WikiList(models.Model):
	title = models.CharField(max_length=128)
	html = models.TextField()
	summary = models.TextField()
	url = models.URLField()

	class Meta:
		verbose_name='Wikipedia List'
		verbose_name_plural='Wikipedia Lists'


class RDF(models.Model):
	wiki_list = models.ForeignKey(WikiList)
	statement = models.TextField()

	class Meta:
		verbose_name='RDF statement'
		verbose_name_plural='RDF statements'


class Link(models.Model):
	wiki_list = models.ForeignKey(WikiList)
	link_name = models.CharField(max_length=128)

	class Meta:
		verbose_name='Referenced Link'
		verbose_name_plural='Referenced Links'


