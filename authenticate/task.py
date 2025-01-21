import os
from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import send_mail
import random
from .models import User
from django.template import loader
from django_celery_beat.models import PeriodicTask
from tictactoe.celery import app
from celery import Celery

@shared_task(bind=True)
def sendEmailTask(self,email):
    subject="Tic-Tac-Toe Account verification."
    otp=random.randint(100000,999999)
    html_message = loader.render_to_string('registrationEmail.html',{'otp':otp})
    send_mail(subject,"", 'Tic-Tac-Toe App', [email], fail_silently=False,html_message=html_message)
    user_obj=User.objects.get(email=email)
    user_obj.otp=otp
    user_obj.save()
    return "DONE"

# Task for sending email for resetting password
@shared_task(bind=True)
def sendForgotEmailTask(self, email):
    subject="Tic-Tac-Toe Reset Password."
    otp=random.randint(100000,999999)
    html_message = loader.render_to_string('forgotPasswordEmail.html',{'otp':otp})
    send_mail(subject,"", 'Tic-Tac-Toe App', [email], fail_silently=False,html_message=html_message)
    user_obj=User.objects.get(email=email)
    user_obj.otp=otp
    user_obj.save()
    return "DONE"

@shared_task(bind=True)
def sendScheduleEmailTask(self,email):
    subject="Tic-Tac-Toe Account verification OTP."
    otp=random.randint(100000,999999)
    html_message = loader.render_to_string('forgotPasswordEmail.html',{'otp':otp})
    send_mail(subject,"", 'Tic-Tac-Toe App', [email], fail_silently=False,html_message=html_message)
    return "DONE"

# to set otp invalid after 5 minutes of sending to user
@shared_task(bind=True)
def invalidateOTP(self,email,name):
    print(name)
    user_obj=User.objects.get(email=email)
    user_obj.otp_validity=False
    user_obj.save()
    periodic_task = PeriodicTask.objects.get(name=name)
    periodic_task.enabled = False
    periodic_task.save()
    return "SET otp Invalid"
