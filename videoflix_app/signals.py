from videoflix_app.tasks import convert_480p
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete 
import os

@receiver(post_save, sender=Video)  
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created and instance.video_file and instance.video_file.name:
        file_path = instance.video_file.path
        if os.path.isfile(file_path):
            convert_480p(file_path)

        # convert_480p(instance.video_file.path)
        # instance.video_file.seek(0)
        # instance.video_file.save(instance.video_file.name, instance.video_file, save=False




@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            
            
            
            
    
            