import random
import string

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate

from .models import CustomUser, Channel
from streamer.models import Playlist

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    channel_name = forms.CharField(max_length=20, help_text='Required.')

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'channel_name')

    def _generate_id(self, length):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def save(self, request):
        user = super(SignupForm, self).save(request)
        new_username = self._generate_id(10)
        while CustomUser.objects.filter(username__exact=new_username).exists():
            new_username = self._generate_id(10)
        user.username = new_username
        user.save()

        new_channel_id = self._generate_id(8)
        while Channel.objects.filter(channel_id=new_channel_id).exists():
            new_channel_id = self._generate_id(8)

        channel = Channel.objects.create(name=request.POST.get('channel_name'), channel_id=new_channel_id, user=user)

        Playlist.objects.create(title='History', channel=channel)
        return user

class SigninForm(forms.Form):
        
    password = forms.CharField(widget=forms.TextInput(attrs={'type' : 'password', 'placeholder' : 'PASSWORD'}))
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'placeholder' : 'E-MAIL'}))

    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            user_cache = authenticate(username=email, password=password)
            if user_cache is None:
                raise forms.ValidationError('Invalid username or password.', code='invalid')
            if not user_cache.email_confirmed:
                raise forms.ValidationError('email address not confirmed, boi!')
        return self.cleaned_data