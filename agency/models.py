from django.db import models
from django.utils.text import slugify

class Agency(models.Model):
    agency_name = models.CharField(max_length=200, blank=False)
    agency_email = models.EmailField(max_length=200, blank=False, unique=True)
    phone_number = models.CharField(max_length=11, blank=False)
    address = models.CharField(max_length=300, null=True)
    agency_logo = models.ImageField(upload_to='agency/logo/', blank=True, default='uploads/default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agency_name} - {self.agency_email}"
    
    

class Notification(models.Model):
    notification = models.CharField(max_length=200, blank=False, unique=True)
    slug = models.SlugField(null=True, default="slug")
    message = models.CharField(max_length=255, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.notification)
        super(Notification, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.notification)
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.notification}"
