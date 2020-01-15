from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email or not password:
            raise ValueError('Users must have email and password.')

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.admin = True
        user.staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(max_length=255, unique=True)
    email_confirmed = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def is_active(self):
        return self.active
    

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    
    def __str__(self):
        return self.email

    def has_perm(self, app_label):
        return self.is_admin

    def has_module_perms(self, module):
        return self.is_admin

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

class Channel(models.Model):
    name = models.CharField(max_length=20)
    channel_id = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name