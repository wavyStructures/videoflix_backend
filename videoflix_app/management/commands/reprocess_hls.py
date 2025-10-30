# videoflix_app/management/commands/reprocess_hls.py

from django.core.management.base import BaseCommand
from videoflix_app.models import Video
import django_rq
from videoflix_app.tasks import run_hls_pipeline

class Command(BaseCommand):
    help = "Re-generate HLS for all videos"

    def handle(self, *args, **options):
        queue = django_rq.get_queue("default")

        count = 0
        for video in Video.objects.all():
            queue.enqueue(run_hls_pipeline, video.id)
            self.stdout.write(f"🔄 Enqueued HLS processing for: {video.title}")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Enqueued HLS pipeline for {count} videos!"))

