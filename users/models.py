from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email or not password:
            raise ValueError('Users must have email and password.')

        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    email_confirmed = models.BooleanField(default=False)


    @property
    def is_staff(self):
        return self.is_staff

    @property
    def is_admin(self):
        return self.is_admin
    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    objects = CustomUserManager()

class Channel(models.Model):
    name = models.CharField(max_length=20)
    channel_id = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name