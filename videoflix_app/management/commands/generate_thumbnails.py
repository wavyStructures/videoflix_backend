from django.core.management.base import BaseCommand
from videoflix_app.models import Video
import django_rq
from videoflix_app.tasks import _generate_thumbnail
import os

class Command(BaseCommand):
    help = "Generate missing thumbnails for videos"

    def handle(self, *args, **options):
        queue = django_rq.get_queue("default")
        restored = 0

        for video in Video.objects.all():
            # Skip if thumbnail file exists already
            if video.thumbnail and os.path.exists(video.thumbnail.path):
                continue

            queue.enqueue(_generate_thumbnail, video.id)
            self.stdout.write(f"🖼️ Regenerating thumbnail: {video.title}")
            restored += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Thumbnails regeneration enqueued for {restored} videos!")
        )
