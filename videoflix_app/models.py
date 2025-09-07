from django.db import models
from datetime import date

class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
        
    hls_master = models.FileField(upload_to="videos/", blank=True, null=True)
    trailer = models.FileField(upload_to="videos/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="videos/", blank=True, null=True)

    category = models.CharField(max_length=50, default="General")
         
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # save original file first

    #     # paths
    #     base_name = os.path.splitext(os.path.basename(self.video_file.name))[0]
    #     output_dir = os.path.join(settings.MEDIA_ROOT, "videos/hls", base_name)
        
    #     # convert to HLS
    #     self.hls_dir = convert_to_hls(self.video_file.path, output_dir, base_name)
        
    #     # generate thumbnail
    #     thumb_path = os.path.join(settings.MEDIA_ROOT, "videos/thumbnails", f"{base_name}.jpg")
    #     self.thumbnail = generate_thumbnail(self.video_file.path, thumb_path)
        
    #     super().save(update_fields=["hls_dir", "thumbnail"])

    def __str__(self):
            return self.title
    