import os
from django.conf import settings
from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model. Exposes all fields of the Video model
    """
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "created_at", "title", "description", "thumbnail_url", "category",]

    def get_thumbnail_url(self, obj):
        """
        Return the absolute URL to the videos thumbnail image.
        Checks for a generated HLS thumbnail first; falls back to the
        uploaded thumbnail if present. Returns an empty string if none found.
        """
        thumb_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(obj.id), 'thumbnail.jpg')
        thumb_url = f"/media/hls/{obj.id}/thumbnail.jpg"

        if os.path.exists(thumb_path):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(thumb_url)
            return thumb_url

        if obj.thumbnail and hasattr(obj.thumbnail, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url

        return ""



