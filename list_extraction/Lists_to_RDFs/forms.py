from django import forms

class TableKeyTest(forms.Form):
	get_columns = (('test','test'),('none','none'),)
	key_column = forms.TypedChoiceField(choices=get_columns)