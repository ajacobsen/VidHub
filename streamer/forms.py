from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Video, VideoFile

class VideoFileForm(forms.ModelForm):

    class Meta:
        model=VideoFile
        fields=["file"]

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.content_type.startswith('video/'):
            raise forms.ValidationError('The file you are uploading may not be a valid video file.')
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Please keep filesize under {}. Current filesize {}'.format(filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file.size)))
        return file

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

