from django import forms

from .models import Video

class VideoForm(forms.ModelForm):
	class Meta:
		model=Video
		fields=["file", "category"]

class EditVideoForm(forms.ModelForm):
	class Meta:
		model = Video
		fields = ['title', 'description', 'thumbnail', 'status']
		widgets = {
			'description' : forms.Textarea(attrs={'class' : 'autoExpand'}),
			'thumbnail' : forms.FileInput(),
			# 'status' : forms.ChoiceField(choices=[('public', 'Public'), ('private', 'Private'), ('unlisted', 'Unlisted')]),
		}

