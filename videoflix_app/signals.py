import os
from pathlib import Path
from django.db.models.signals import post_save, post_delete 
from django.dispatch import receiver
from django.conf import settings
from .models import Video
from .tasks import convert_to_hls, generate_thumbnail


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Runs HLS conversion after a new video is uploaded.
    Safely updates model fields for frontend compatibility.
    """
    if created and instance.video_file:
        print(f"Running HLS pipeline for: {instance.video_file.path}")

        try:
            # Convert video to HLS + generate master playlist, trailer, thumbnail
            master_path = convert_to_hls(
                source_path=instance.video_file.path,
                video_id=instance.id,
                make_trailer=True,
                make_thumbnail=True,
            )

            # Update master playlist field safely
            if master_path and os.path.exists(master_path):
                instance.hls_master.name = os.path.relpath(master_path, settings.MEDIA_ROOT)

            # Update trailer field for frontend: point to 480p/index.m3u8
            hls_480_index = Path(settings.MEDIA_ROOT) / "hls" / str(instance.id) / "480p" / "index.m3u8"
            if hls_480_index.exists():
                instance.trailer.name = os.path.relpath(hls_480_index, settings.MEDIA_ROOT)

            # Update thumbnail field
            thumb_path = Path(settings.MEDIA_ROOT) / "hls" / str(instance.id) / "thumbnail.jpg"
            if thumb_path.exists():
                instance.thumbnail.name = os.path.relpath(thumb_path, settings.MEDIA_ROOT)

            # Save updates
            instance.save(update_fields=["hls_master", "trailer", "thumbnail"])

        except Exception as e:
            print(f"Error running HLS conversion: {e}")

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes files from filesystem when the Video object is deleted.
    """
    # Delete uploaded video file
    if instance.video_file and instance.video_file.name:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

    # Delete HLS folder
    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(instance.id)
    if hls_dir.exists() and hls_dir.is_dir():
        for root, dirs, files in os.walk(hls_dir, topdown=False):
            for name in files:
                os.remove(Path(root) / name)
            for name in dirs:
                os.rmdir(Path(root) / name)
        hls_dir.rmdir()


        
    
            