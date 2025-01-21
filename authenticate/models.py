from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.
class User(AbstractUser):
    username=None
    email=models.EmailField(unique=True)
    verification_status=models.CharField(max_length=20,default='pending')
    otp =models.CharField(max_length=6, null=True)
    otp_validity =models.BooleanField(default=False)
    is_user=models.BooleanField(default=True)
    is_doctor=models.BooleanField(default=False)
    resetToken=models.CharField(max_length=50,default="none")

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=[]
    objects=UserManager()

class UserProfile(models.Model):
    user_profile_id=models.AutoField(primary_key=True)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_pics',default='default.jpg')
    name = models.CharField(max_length=100)