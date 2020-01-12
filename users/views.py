from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.views import View

from .forms import SignupForm, SigninForm
from .models import CustomUser
from .tokens import account_activation_token

class SignupView(View):

    def get(self, request):
        form = SignupForm()
        return render(request, 'users/signup.html', {'form' : form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            domain = settings.DOMAIN
            subject = 'Activate Your TRACLE Account!'
            message = render_to_string('users/account_activation_email.html', {
                'user' : user,
                'domain' : domain,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
            user.email_user(subject, message)
            return redirect('users:login')
        else:
            return render(request, 'users/signup.html', {'form' : form})

class LoginView(View):

    def get(self, request):
        form = SigninForm()
        return render(request, 'users/login.html', {'form' : form})

    def post(self, request):
        form = SigninForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('streamer:index')

        return render(request, 'users/login.html', {'form' : form})

class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('streamer:index')

class ActivateView(View):

    def get(self, request, key, token):
        try:
            uid = force_text(urlsafe_base64_decode(key))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.email_confirmed = True
            user.save()
            return redirect('users:login')
        else:
            return render(request, 'users/account_activation_invalid.html')