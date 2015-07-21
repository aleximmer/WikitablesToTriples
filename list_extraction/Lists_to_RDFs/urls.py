from django.conf.urls import patterns, url

from Lists_to_RDFs import views

urlpatterns = patterns('',
	url(r'Tool/', views.show_final_tool, name='Lists to RDFs'),
	url(r'GetTable/', views.get_table, name='Lists to RDFs - Get table informations'),
	url(r'GetRDFs/', views.get_rdfs, name='Lists to RDFs - Get tables rdf triples'),
	url(r'KeyForm/', views.init_testing, name='Key Extraction Form'),
	url(r'KeyTest/', views.get_table_key, name='Key Test'),
	url(r'KeyResult/', views.get_correct_key, name='Key Test Result'),
	url(r'KeyPrecRec/', views.get_prec_rec, name='Calculate Precision and Recall'))
