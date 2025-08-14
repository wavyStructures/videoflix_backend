from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        # TODO  have thumbnails saved in media/thumbnails/<video_id>.jpg
        request = self.context.get('request')
        return request.build_absolute_uri(f'/media/thumbnails/{obj.id}.jpg')


