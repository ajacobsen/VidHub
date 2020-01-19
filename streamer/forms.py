
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Video, VideoFile

class VideoFileForm(forms.ModelForm):
	class Meta:
		model=VideoFile
		fields=["file"]

class VideoForm(forms.ModelForm):
	class Meta:
		model = Video
		fields = ['title', 'description', 'category', 'thumbnail', 'status']

class EditVideoForm(forms.ModelForm):
	class Meta:
		model = Video
		fields = ['title', 'description', 'thumbnail', 'status']
		widgets = {
			'description' : forms.Textarea(attrs={'class' : 'autoExpand'}),
			'thumbnail' : forms.FileInput(),
			# 'status' : forms.ChoiceField(choices=[('public', 'Public'), ('private', 'Private'), ('unlisted', 'Unlisted')]),
		}

