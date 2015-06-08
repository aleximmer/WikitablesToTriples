from django.conf.urls import patterns, url

from Lists_to_RDFs import views

urlpatterns = patterns('',
	url(r'KeyExtraction/', views.testKeyExtraction, name='Test Key Extraction'),
	url(r'KeyForm/', views.get_hum_col, name='Key Extraction Form'),
	url(r'KeyTestStart/', views.init_testing, name='Init Testing'),
	url(r'KeyTest/', views.get_table_key, name='Key Test'),
	url(r'KeyResult/', views.get_correct_key, name='Key Test Result'),)