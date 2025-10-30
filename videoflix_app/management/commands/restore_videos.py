# videoflix_app/management/commands/restore_videos.py

import os
from django.core.management.base import BaseCommand
from videoflix_app.models import Video

class Command(BaseCommand):
    help = "Re-create Video objects from existing media/video files"

    def handle(self, *args, **options):
        media_path = "media/video/"
        
        if not os.path.exists(media_path):
            self.stdout.write(self.style.ERROR("❌ media/video/ does not exist"))
            return

        restored = 0

        for filename in os.listdir(media_path):
            file_path = os.path.join(media_path, filename)

            # Skip directories (e.g. thumbnails or hls folders)
            if not os.path.isfile(file_path):
                continue

            video_rel_path = f"video/{filename}"

            video, created = Video.objects.get_or_create(
                video_file=video_rel_path,
                defaults={"title": os.path.splitext(filename)[0]}
            )

            if created:
                restored += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Restored: {filename}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Done! Restored {restored} missing video entries ✅")
        )
