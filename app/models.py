from django.db import models

# Create your models here.



class JobDescription(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')