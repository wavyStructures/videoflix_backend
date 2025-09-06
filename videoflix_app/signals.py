from videoflix_app.tasks import convert_480p
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete 
from django.conf import settings
from .models import Video
from .tasks import convert_to_hls, generate_thumbnail
import os


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print("post_save fired")

    if created and instance.video_file:
        base_name = os.path.splitext(os.path.basename(instance.video_file.name))[0]
        hls_output_dir = os.path.join(settings.MEDIA_ROOT, "videos/hls", base_name)
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "videos/thumbnails", f"{base_name}.jpg")

        # Convert to HLS
        instance.hls_dir = convert_to_hls(instance.video_file.path, hls_output_dir, base_name)

        # Generate thumbnail
        instance.thumbnail = generate_thumbnail(instance.video_file.path, thumbnail_path)

        # Save updated fields
        instance.save(update_fields=["hls_dir", "thumbnail"])


    if created and instance.video_file and instance.video_file.name:
        file_path = instance.video_file.path
        print(f"File path is: {file_path}")
        if os.path.isfile(file_path):
            print("File exists, converting...")
            convert_480p(file_path)
        else:
            print("File does not exist yet")
            
        # convert_480p(instance.video_file.path)
        # instance.video_file.seek(0)
        # instance.video_file.save(instance.video_file.name, instance.video_file, save=False


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.video_file and instance.video_file.name:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            
            
            
            
    
            