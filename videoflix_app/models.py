from django.db import models
from datetime import date

class Video(models.Model):
    """
    Represents a video object in the system.
    """
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    video_file = models.FileField(upload_to='videos/', max_length=500, blank=True, null=True)
        
    hls_master = models.FileField(upload_to="videos/", max_length=500, blank=True, null=True)
    trailer = models.FileField(upload_to="videos/", max_length=500, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="videos/", max_length=500, blank=True, null=True)

    category = models.CharField(max_length=50, default="General")
         
    def __str__(self):
            return self.title
    