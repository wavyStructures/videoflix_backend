from django.db import models
from datetime import date


def video_upload_path(instance, filename):
    return f"video/{filename}"

class Video(models.Model):
    """
    Represents a video object in the system.
    """

    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80, unique=True)
    description = models.TextField(max_length=500)

    video_file = models.FileField(upload_to=video_upload_path, max_length=500, blank=True, null=True)
    category = models.CharField(max_length=50, default="General")
        
    hls_master = models.FileField(upload_to="video/hls", max_length=500, blank=True, null=True)
    trailer = models.FileField(upload_to="video/trailer", max_length=500, blank=True, null=True)
    thumbnail_url = models.ImageField(upload_to="thumbnails/", max_length=500, blank=True, null=True)

         
    def __str__(self):
            return self.title
    



