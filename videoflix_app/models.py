from django.db import models
from datetime import date

class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    # video_url = models.URLField()
    # thumbnail_url = models.URLField()
    
    def __str__(self):
        return self.title
    
    