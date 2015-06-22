from django.conf.urls import patterns, url

from Lists_to_RDFs import views

urlpatterns = patterns('',
	url(r'KeyForm/', views.init_testing, name='Key Extraction Form'),
	url(r'KeyTest/', views.get_table_key, name='Key Test'),
	url(r'KeyResult/', views.get_correct_key, name='Key Test Result'),
	url(r'KeyPrecRec/', views.get_prec_rec, name='Calculate Precision and Recall'))