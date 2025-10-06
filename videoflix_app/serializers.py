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
        request = self.context.get("request")
        if obj.thumbnail and hasattr(obj.thumbnail, "url"):
            return request.build_absolute_uri(obj.thumbnail.url)
        return ""



