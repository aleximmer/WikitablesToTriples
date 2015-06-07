from django.conf.urls import patterns, url

from Lists_to_RDFs import views

urlpatterns = patterns('',
	url(r'KeyExtraction/', views.testKeyExtraction, name='Test Key Extraction'),)