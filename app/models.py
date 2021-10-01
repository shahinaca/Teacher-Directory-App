from django.db import models

# Create your models here.
class Teacher(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.CharField(max_length=255, default='null')
    email_address = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    room_number = models.CharField(max_length=20)
    subjects_taught = models.TextField()
    profile_path = models.CharField(max_length=255, default='null')

# Create your models here.
class UploadLog(models.Model):
    teachers_details = models.FileField()
    image_details = models.FileField(default=False)