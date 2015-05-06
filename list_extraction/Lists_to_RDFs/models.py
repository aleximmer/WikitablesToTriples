from django.db import models

# Create your models here.

class WikiList(models.Model):
	title = models.CharField(max_length=128)
	html = models.TextField()

class RDF(models.Model):
	wiki_list = models.ForeignKey(WikiList)
	statement = models.TextField()

